"""
AnkerMake MQTT Adapter
This module is responsible for handling the MQTT messages from the AnkerMake printer and updating the AnkerData object.

In other words, this module is the "brain" of the AnkerMake integration.
"""
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

from .anker_models import (CommandTypes,
                           FilamentType,
                           FILAMENT_WEIGHT_175,
                           FILAMENT_DENSITY,
                           AnkerUnhandledCommandException,
                           AnkerStatus,
                           NOZZLE_TYPES,
                           ERROR_CODES)

_LOGGER = getLogger(__name__)

RESET_STATES = [AnkerStatus.OFFLINE, AnkerStatus.IDLE]


@dataclass
class AnkerData:
    _timezone: datetime.tzinfo = None
    _last_heartbeat: datetime = None
    _status: AnkerStatus = AnkerStatus.OFFLINE
    _old_status: AnkerStatus = None
    _old_job_name: str = ""
    job_name: str = ""
    image: str = ""

    paused: bool = False

    error_message: str = ""
    error_level: str = ""
    error_ext: str = ""

    progress: float = 0
    elapsed_time: int = 0
    remaining_time: int = 0
    total_time: int = 0

    fan_speed: int = 0

    nozzle_type: str = NOZZLE_TYPES.get("0")  # TODO: Figure out what nozzle_types are available
    bed_leveled: bool = True

    print_start_time: datetime = None
    print_target_time: datetime = None

    motor_locked: bool = False
    ai_enabled: bool = False

    # TODO: Currently no message for filament type except for error messages (afaik). Currently derived from filename.
    filament: str = FilamentType.UNKNOWN.value

    filament_used: float = 0

    current_speed: int = 0
    max_speed: int = 500

    current_layer: int = 0
    total_layers: int = 0

    hotend_temp: float = 0
    target_hotend_temp: float = 0
    bed_temp: float = 0
    target_bed_temp: float = 0

    def __post_init__(self):
        """Initialize the AnkerData object."""
        # Set the last heartbeat to the epoch (so that the printer is considered offline until the first heartbeat)
        self._last_heartbeat = datetime(1970, 1, 1, tzinfo=self._timezone)

    def _reset(self):
        """Reset every value except for those with leading underscores to their default value"""
        [setattr(self, key, getattr(self.__class__, key))
         for key, value in self.__dict__.items()
         if not key.startswith("_")]

    def _pulse(self):
        """Pulse the printer's heartbeat. (Used to determine if the printer is online)"""
        self._last_heartbeat = datetime.now(tz=self._timezone)

    @property
    def online(self) -> bool:
        """Returns True if the printer is online."""
        # TODO: Make this less taxing on the system (checks n(entities) times per update cycle)
        return self._last_heartbeat > datetime.now(tz=self._timezone) - timedelta(seconds=30)

    @property
    def printing(self) -> bool:
        """Returns True if the printer is currently printing."""
        return self.job_name != "" or self.progress

    @property
    def filament_weight(self) -> float:
        """Returns the weight of the filament used in grams."""
        # PLA is the default filament type (if the filament type is unknown)
        weight = float(FILAMENT_WEIGHT_175.get(self.filament,
                                               FILAMENT_WEIGHT_175.get(FilamentType.PLA.value))) * self.filament_used
        return round(weight, 2)

    @property
    def filament_density(self) -> float:
        """Returns the density of the filament in g/cm^3."""
        density = self.filament_weight / FILAMENT_DENSITY.get(self.filament,
                                                              FILAMENT_DENSITY.get(FilamentType.PLA.value))
        return round(density, 2)

    def _new_status_handler(self, new_status: AnkerStatus):
        """Handler for new status changes."""
        # If the status is the same as the old status, return
        if new_status == self._old_status:
            return

        self._update_target_time()

        # Reset the error message if the status is no longer an error
        if self._old_status == AnkerStatus.ERROR:
            self._remove_error()

        # Reset the data if the status is one of the reset states
        if new_status in RESET_STATES:
            self._reset()

        self._old_status = new_status

    @property
    def status(self) -> str:
        """Returns the current state of the printer."""
        status = AnkerStatus.PRINTING

        # Check if the printer is heating up
        is_heating_hotend = self.target_hotend_temp - 5 > self.hotend_temp > 30
        is_heating_bed = self.target_bed_temp - 2 > self.bed_temp > 30

        if not self.online:
            status = AnkerStatus.OFFLINE
        elif self.in_error_state:
            status = AnkerStatus.ERROR
        elif self.paused:
            status = AnkerStatus.PAUSED
        elif not self.progress and (is_heating_hotend or is_heating_bed):
            status = AnkerStatus.PREHEATING
        elif self.progress == 100:
            status = AnkerStatus.FINISHED
        elif not self.printing:
            status = AnkerStatus.IDLE

        self._new_status_handler(status)
        return status.value

    def _update_target_time(self):
        """Should not call this too often (on state change / new print job)"""
        if self.remaining_time:
            self.print_target_time = datetime.now(tz=self._timezone) + timedelta(seconds=self.remaining_time)

    def _update_filament(self):
        """Should not call this too often (new print job)"""
        # Get Filament from filename (assume it is the last filament mentioned in the filename)
        matches = re.findall(FilamentType.options_regex(), self.job_name, re.IGNORECASE)
        # Make sure the last match is a lone word (e.g. "PLA" and not "PLANET")
        while matches and not re.search(rf'(?:\b|_){matches[-1]}(?:\b|_)', self.job_name, re.IGNORECASE):
            matches.pop()
        if matches:
            self.filament = FilamentType.upper_dict().get(matches[-1].upper(), FilamentType.UNKNOWN.value)
        else:
            self.filament = FilamentType.UNKNOWN.value

    def _new_print_job(self):
        """Things to do when a new print job is registered (when the job_name changes)"""
        self._remove_error()
        self.print_start_time = datetime.now(tz=self._timezone) - timedelta(seconds=self.elapsed_time)
        self._update_target_time()
        self._update_filament()

    def _new_job_handler(self):
        """Handler for new print jobs"""
        if self.job_name != self._old_job_name:
            self._new_print_job()

    @property
    def in_error_state(self) -> bool:
        """Returns True if the printer has an error."""
        return self.error_message != ""

    def _remove_error(self):
        """Removes the error from the AnkerData object, allowing the status to change."""
        self.error_message = ""
        self.error_level = ""

    def update(self, websocket_message: dict):
        """Update the AnkerData object with a new message from the AnkerMake printer."""
        command_type = websocket_message.get("commandType")
        match command_type:
            # Print schedule is broadcast at fixed intervals (every 5 seconds or so)
            # Not to be confused with print started (unused) that contains mostly the same data
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SCHEDULE.value:
                # Update the status
                self.job_name = websocket_message.get("name")
                self.image = websocket_message.get("img")

                progress = websocket_message.get("progress") / 100
                self.progress = round(progress, 1)

                _elapsed_time = int(websocket_message.get("totalTime"))
                _remaining_time = int(websocket_message.get("time"))
                self.elapsed_time = _elapsed_time
                self.remaining_time = _remaining_time
                self.total_time = _elapsed_time + _remaining_time

                self.ai_enabled = websocket_message.get("aiFlag") == 1

                filament_used = websocket_message.get("filamentUsed") / 1000  # Get meters (from mm)
                self.filament_used = round(filament_used, 2)

                # Register new print job (only on this event)
                self._new_job_handler()
                self._old_job_name = self.job_name

            # Model Layer is broadcast every layer change
            case CommandTypes.ZZ_MQTT_CMD_MODEL_LAYER.value:
                self.current_layer = websocket_message.get("real_print_layer")
                self.total_layers = websocket_message.get("total_layer")

            # Nozzle temp gets broadcast with fixed intervals (every 5 seconds or so)
            case CommandTypes.ZZ_MQTT_CMD_NOZZLE_TEMP.value:
                self._pulse()  # _pulse goes here since this is a reliable mqtt message that doesn't get spammed too much

                hotend_temp = websocket_message.get("currentTemp") / 100
                target_hotend_temp = websocket_message.get("targetTemp") / 100
                self.hotend_temp = round(hotend_temp, 1)
                self.target_hotend_temp = round(target_hotend_temp, 1)

            # Fan speed gets broadcast.. when the fan speed changes?
            case CommandTypes.ZZ_MQTT_CMD_FAN_SPEED.value:
                self.fan_speed = websocket_message.get("value")

            # Motor lock gets broadcast presumably when the motor is locked/unlocked (on print start)
            case CommandTypes.ZZ_MQTT_CMD_MOTOR_LOCK.value:
                self.motor_locked = websocket_message.get("lock") == 1

            # Hotbed temp gets broadcast with fixed intervals (every 5 seconds or so)
            case CommandTypes.ZZ_MQTT_CMD_HOTBED_TEMP.value:
                bed_temp = websocket_message.get("currentTemp") / 100  # Divide by 100 to get the correct value
                target_bed_temp = websocket_message.get("targetTemp") / 100  # Divide by 100 to get the correct value
                self.bed_temp = round(bed_temp, 1)
                self.target_bed_temp = round(target_bed_temp, 1)

            # Print speed gets broadcast sporadically?, stays the same even when paused
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SPEED.value:
                self.current_speed = websocket_message.get("value")

            # A _message_ gets sent when the printer is paused, but it doesn't contain any relevant data
            # No idea if this can be sent in other situations as well
            case CommandTypes.ZZ_MQTT_CMD_PRINT_CONTROL.value:
                self.paused = not self.paused  # Toggle the paused state (No relevant data in the message :/)

            # Max print speed gets broadcast sporadically?
            case CommandTypes.TEMP_MAX_PRINT_SPEED.value:
                self.max_speed = websocket_message.get("max_print_speed")

            # Nozzle type is broadcast shortly after a print job is _properly_ started
            case CommandTypes.TEMP_NOZZLE_TYPE.value:
                self.nozzle_type = NOZZLE_TYPES.get(str(websocket_message.get("nozzle_type")),
                                                    str(websocket_message.get("nozzle_type")))

            # Auto-leveling sends a message with isLeveled: 1 (and presumably isLeveled: 0 when it's not leveled)
            case CommandTypes.TEMP_IS_LEVELED.value:
                self.bed_leveled = websocket_message.get("isLeveled") == 1

            # Errors (?)
            case CommandTypes.TEMP_ERROR_CODE.value:
                self.error_level = websocket_message.get("errorLevel")
                self.error_message = ERROR_CODES.get(websocket_message.get("errorCode"),
                                                     websocket_message.get("errorCode"))
                if self.error_message not in ERROR_CODES.values():
                    _LOGGER.error(
                        f"Unknown error occured: {self.error_message}. Please open a github issue with a description of what you were doing when this error occurred, and please look in the AnkerMake app for a proper error message. Include this: (Received message: {websocket_message})")

            # If the command_type is not handled, raise an exception (unless we know it's not used)
            case _:
                if command_type not in CommandTypes:
                    _LOGGER.error(f"Unknown command_type: {command_type} ({websocket_message})")
                    raise AnkerUnhandledCommandException(f"Unknown command_type: {command_type} ({websocket_message})")
