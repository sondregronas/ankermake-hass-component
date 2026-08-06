"""
AnkerMake MQTT Adapter
This module is responsible for handling the MQTT messages from the AnkerMake printer and updating the AnkerData object.

In other words, this module is the "brain" of the AnkerMake integration.
"""

import os
import re
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger

from .anker_models import (
    CommandTypes,
    FilamentType,
    FILAMENT_WEIGHT_175,
    FILAMENT_DENSITY,
    AnkerUnhandledCommandException,
    AnkerStatus,
    NOZZLE_TYPES,
    ERROR_CODES,
)

_LOGGER = getLogger(__name__)
if os.environ.get("ANKERMAKE_DEBUG", False):
    _LOGGER.setLevel("DEBUG")

RESET_STATES = [
    AnkerStatus.OFFLINE,
    AnkerStatus.IDLE,
    AnkerStatus.CHANGING_FILAMENT,
]


@dataclass
class AnkerData:
    _timezone: datetime.tzinfo = None  # Defined in __init__.py
    _api_status: dict = None  # Updated via __init__.py

    _last_heartbeat: datetime = None
    _status: AnkerStatus = AnkerStatus.OFFLINE
    _old_status: AnkerStatus = None

    _job_active: bool = False
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

    nozzle_type: str = NOZZLE_TYPES.get(
        "0"
    )  # TODO: Figure out what nozzle_types are available
    bed_leveled: bool = True

    print_start_time: datetime = None
    print_target_time: datetime = None

    motor_locked: bool = False

    ai_enabled: bool = False
    ai_level: int = 0
    ai_pause_print: bool = False
    ai_data_collection: bool = False

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
        [
            setattr(self, key, getattr(self.__class__, key))
            for key, value in self.__dict__.items()
            if not key.startswith("_")
            # Skip keys ending with _temp unless the new state is OFFLINE (to avoid clearing target temps mid-print)
            and not (key.endswith("_temp") and self._status != AnkerStatus.OFFLINE)
        ]
        # No further updates arrive once offline, so clear this explicitly
        self._job_active = False

    def _pulse(self):
        """Pulse the printer's heartbeat. (Used to determine if the printer is online)"""
        self._last_heartbeat = datetime.now(tz=self._timezone)

    @property
    def online(self) -> bool:
        """Returns True if the printer is online."""
        # TODO: Make this less taxing on the system (checks n(entities) times per update cycle)
        return self._last_heartbeat > datetime.now(tz=self._timezone) - timedelta(
            seconds=30
        )

    @property
    def printing(self) -> bool:
        """Returns True if the printer is actively advancing through a print job."""
        return 0 < self.progress < 100

    @property
    def filament_weight(self) -> float:
        """Returns the weight of the filament used in grams."""
        # PLA is the default filament type (if the filament type is unknown)
        weight = (
            float(
                FILAMENT_WEIGHT_175.get(
                    self.filament, FILAMENT_WEIGHT_175.get(FilamentType.PLA.value)
                )
            )
            * self.filament_used
        )
        return round(weight, 2)

    @property
    def filament_density(self) -> float:
        """Returns the density of the filament in g/cm^3."""
        density = self.filament_weight / FILAMENT_DENSITY.get(
            self.filament, FILAMENT_DENSITY.get(FilamentType.PLA.value)
        )
        return round(density, 2)

    def _new_status_handler(self, new_status: AnkerStatus) -> AnkerStatus:
        """Handler for new status changes."""
        status = new_status

        # If the status is the same as the old status, return the same status
        if status == self._old_status:
            return status

        self._update_target_time()

        # Reset the error message if we are moving from an errored state
        if self._old_status == AnkerStatus.ERROR:
            self._remove_error()

        # Reset all data if the status is one of the reset states
        if status in RESET_STATES:
            self._reset()

        # Clear target temps once done, this step might be redundant.
        if status == AnkerStatus.FINISHED:
            self._clear_target_temps()

        self._old_status = status
        return status

    @property
    def is_heating_hotend(self, threshold: float = 3) -> bool:
        """Returns True if the hotend is actively heating."""
        return (
            self.target_hotend_temp
            and abs(self.target_hotend_temp - self.hotend_temp) > threshold
        )

    @property
    def is_heating_bed(self, threshold: float = 2) -> bool:
        """Returns True if the bed is actively heating."""
        return (
            self.target_bed_temp
            and abs(self.target_bed_temp - self.bed_temp) > threshold
        )

    @property
    def status(self) -> str:
        """Returns the current state of the printer."""
        is_heating = self.is_heating_hotend or self.is_heating_bed
        # We can detect filament changing when hotend is heating and the bed temperature target is nil
        is_changing_filament = self.target_hotend_temp and not self.target_bed_temp

        # Targets are only set by the printer once a job is heating up, so reaching
        # them (without printing yet) means we're in the homing step
        targets_set = self.target_hotend_temp > 0 and self.target_bed_temp > 0
        reached_targets = targets_set and not is_heating

        if not self.online:
            status = AnkerStatus.OFFLINE
        elif self.in_error_state:
            status = AnkerStatus.ERROR
        elif self.paused:
            status = AnkerStatus.PAUSED
        elif is_changing_filament:
            status = AnkerStatus.CHANGING_FILAMENT
        elif self.progress == 100:
            status = AnkerStatus.FINISHED
        elif (
            not self.progress and self._old_status == AnkerStatus.HOMING and is_heating
        ):
            # Target temp can bump up mid-homing; don't fall back to preheating
            status = AnkerStatus.HOMING
        elif not self.progress and is_heating:
            status = AnkerStatus.PREHEATING
        elif not self.progress and reached_targets:
            status = AnkerStatus.HOMING
        elif not self.progress and self._old_status == AnkerStatus.FINISHED:
            status = AnkerStatus.FINISHED
        elif self.printing:
            status = AnkerStatus.PRINTING
        else:
            status = AnkerStatus.IDLE

        return self._new_status_handler(status).value

    def _update_target_time(self):
        """Should not call this too often (on state change / new print job)"""
        if self.remaining_time:
            self.print_target_time = datetime.now(tz=self._timezone) + timedelta(
                seconds=self.remaining_time
            )

    def _update_filament(self):
        """Should not call this too often (new print job)"""
        # Get Filament from filename (assume it is the last filament mentioned in the filename)
        matches = re.findall(FilamentType.options_regex(), self.job_name, re.IGNORECASE)
        # Make sure the last match is a lone word (e.g. "PLA" and not "PLANET")
        while matches and not re.search(
            rf"(?:\b|_){matches[-1]}(?:\b|_)", self.job_name, re.IGNORECASE
        ):
            matches.pop()
        if matches:
            self.filament = FilamentType.upper_dict().get(
                matches[-1].upper(), FilamentType.UNKNOWN.value
            )
        else:
            self.filament = FilamentType.UNKNOWN.value

    def _new_print_job(self):
        """Things to do when a new print job is registered"""
        self._remove_error()
        self.print_start_time = datetime.now(tz=self._timezone) - timedelta(
            seconds=self.elapsed_time
        )
        self._update_target_time()
        self._update_filament()

    @property
    def in_error_state(self) -> bool:
        """Returns True if the printer has an error."""
        return self.error_message != ""

    def _remove_error(self):
        """Removes the error from the AnkerData object, allowing the status to change."""
        self.error_message = ""
        self.error_level = ""

    def _clear_target_temps(self):
        """Clears stale target temps."""
        self.target_hotend_temp = 0
        self.target_bed_temp = 0

    @property
    def api_service_possible_states(self) -> list:
        return list(self._api_status.get("possible_states", {}).keys()) + [
            "Unavailable"
        ]

    def get_api_version_value(self, key: str) -> str:
        return self._api_status.get("version", {}).get(key, "Unavailable")

    def get_api_service_status(self, service: str) -> str:
        return (
            self._api_status.get("services", {})
            .get(service, {})
            .get("state", "Unavailable")
        )

    def get_api_service_online(self, service: str) -> bool:
        return (
            self._api_status.get("services", {}).get(service, {}).get("online", False)
        )

    def update(self, websocket_message: dict):
        """Update the AnkerData object with a new message from the AnkerMake printer."""
        wm = websocket_message
        command_type = wm.get("commandType")

        # Update heartbeat
        self._pulse()

        # Debug logging for all messages except those that spam
        if command_type not in [1000, 1001, 1003, 1004, 1006, 1081, 1084]:
            _LOGGER.debug(f"Received message: {wm}")
        match command_type:
            # Print schedule is broadcast at fixed intervals (every 5 seconds or so)
            # Not to be confused with print started (unused) that contains mostly the same data
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SCHEDULE.value:
                new_job_name = wm.get("name", "")
                job_active = bool(new_job_name)
                _elapsed_time = int(wm.get("totalTime", 0))
                _remaining_time = int(wm.get("time", 0))
                # A reprint never toggles job_active false->true, so also treat a
                # reset in elapsed time as a new job
                new_job_started = job_active and (
                    not self._job_active or _elapsed_time < self.elapsed_time
                )
                self._job_active = job_active
                self.job_name = new_job_name or self.job_name  # sticky
                self.image = wm.get("img")

                if not job_active:
                    self._clear_target_temps()

                progress = math.floor(wm.get("progress", 0)) / 100
                # Only jump from 100->0 if a new job started
                if new_job_started or not (progress == 0 and self.progress == 100):
                    self.progress = progress

                self.elapsed_time = _elapsed_time
                self.remaining_time = _remaining_time
                self.total_time = _elapsed_time + _remaining_time

                # Not every firmware sends the AI fields, so keep the previous value when absent
                self.ai_enabled = (
                    max(
                        wm.get("aiFlag", 0),
                        wm.get("AISwitch", 0),
                    )
                    == 1
                )
                self.ai_level = wm.get("AISensitivity", self.ai_level)
                self.ai_pause_print = wm.get("AIPausePrint", self.ai_pause_print) == 1
                self.ai_data_collection = (
                    wm.get("AIJoinImproving", self.ai_data_collection) == 1
                )

                filament_used = wm.get("filamentUsed", 0) / 1000  # Get meters (from mm)
                self.filament_used = round(filament_used, 2)

                # Register new print job (only on this event)
                if new_job_started:
                    self._new_print_job()

            # Model Layer is broadcast every layer change
            case CommandTypes.ZZ_MQTT_CMD_MODEL_LAYER.value:
                self.current_layer = wm.get("real_print_layer")
                self.total_layers = wm.get("total_layer")

            # Nozzle temp gets broadcast with fixed intervals (every 5 seconds or so)
            case CommandTypes.ZZ_MQTT_CMD_NOZZLE_TEMP.value:
                # currentTemp/targetTemp are sent separately: keep the last known value when absent
                if "currentTemp" in wm:
                    self.hotend_temp = round(wm["currentTemp"] / 100, 1)
                if "targetTemp" in wm:
                    self.target_hotend_temp = round(wm["targetTemp"] / 100, 1)

            # Fan speed gets broadcast... when the fan speed changes?
            case CommandTypes.ZZ_MQTT_CMD_FAN_SPEED.value:
                self.fan_speed = wm.get("value")

            # Motor lock gets broadcast presumably when the motor is locked/unlocked (on print start)
            case CommandTypes.ZZ_MQTT_CMD_MOTOR_LOCK.value:
                self.motor_locked = wm.get("lock") == 1

            # Hotbed temp gets broadcast with fixed intervals (every 5 seconds or so)
            case CommandTypes.ZZ_MQTT_CMD_HOTBED_TEMP.value:
                # Divide by 100 to get the correct value; keep the last known value when absent
                if "currentTemp" in wm:
                    self.bed_temp = round(wm["currentTemp"] / 100, 1)
                if "targetTemp" in wm:
                    self.target_bed_temp = round(wm["targetTemp"] / 100, 1)

            # Print speed gets broadcast sporadically?, stays the same even when paused
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SPEED.value:
                self.current_speed = wm.get("value")

            # A _message_ gets sent when the printer is paused, but it doesn't contain any relevant data
            # No idea if this can be sent in other situations as well
            case CommandTypes.ZZ_MQTT_CMD_PRINT_CONTROL.value:
                self.paused = (
                    not self.paused
                )  # Toggle the paused state (No relevant data in the message :/)

            # Max print speed gets broadcast sporadically?
            case CommandTypes.TEMP_MAX_PRINT_SPEED.value:
                self.max_speed = wm.get("max_print_speed")

            # Nozzle type is broadcast shortly after a print job is _properly_ started
            case CommandTypes.TEMP_NOZZLE_TYPE.value:
                self.nozzle_type = NOZZLE_TYPES.get(
                    str(wm.get("nozzle_type")),
                    str(wm.get("nozzle_type")),
                )

            # Auto-leveling sends a message with isLeveled: 1 (and presumably isLeveled: 0 when it's not leveled)
            case CommandTypes.TEMP_IS_LEVELED.value:
                self.bed_leveled = wm.get("isLeveled") == 1

            # When the STOP button is pressed, this message is sent
            case CommandTypes.TEMP_PRINT_STOPPED.value:
                # Resetting for now, which will set state to IDLE
                self._reset()

            # Errors (?)
            case CommandTypes.TEMP_ERROR_CODE.value:
                self.error_level = wm.get("errorLevel")
                self.error_message = ERROR_CODES.get(
                    wm.get("errorCode"),
                    wm.get("errorCode"),
                )
                if self.error_message not in ERROR_CODES.values():
                    _LOGGER.error(
                        f"Unknown error occured: {self.error_message}. Please open a github issue with a description of what you were doing when this error occurred, and please look in the AnkerMake app for a proper error message. Include this: (Received message: {wm})"
                    )

            # If the command_type is not handled, raise an exception (unless we know it's not used)
            case _:
                if command_type not in CommandTypes:
                    _LOGGER.error(f"Unknown command_type: {command_type} ({wm})")
                    raise AnkerUnhandledCommandException(
                        f"Unknown command_type: {command_type} ({wm})"
                    )
