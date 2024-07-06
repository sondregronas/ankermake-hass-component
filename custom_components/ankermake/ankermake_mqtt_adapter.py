"""
AnkerMake MQTT Adapter
This module is responsible for handling the MQTT messages from the AnkerMake printer and updating the AnkerData object.

In other words, this module is the "brain" of the AnkerMake integration.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from logging import getLogger

_LOGGER = getLogger(__name__)


class AnkerException(BaseException):
    ...


class AnkerUnhandledCommandException(AnkerException):
    ...


class CommandTypes(Enum):
    """Glossary: https://github.com/Ankermgmt/ankermake-m5-research/blob/master/mqtt/message-types.md"""
    ZZ_MQTT_CMD_EVENT_NOTIFY = 1000
    ZZ_MQTT_CMD_PRINT_SCHEDULE = 1001
    ZZ_MQTT_CMD_FIRMWARE_VERSION = 1002  # Not used
    ZZ_MQTT_CMD_NOZZLE_TEMP = 1003
    ZZ_MQTT_CMD_HOTBED_TEMP = 1004
    ZZ_MQTT_CMD_FAN_SPEED = 1005  # Not used
    ZZ_MQTT_CMD_PRINT_SPEED = 1006
    ZZ_MQTT_CMD_AUTO_LEVELING = 1007  # Not used
    ZZ_MQTT_CMD_PRINT_CONTROL = 1008  # Not used
    ZZ_MQTT_CMD_FILE_LIST_REQUEST = 1009  # Not used
    ZZ_MQTT_CMD_GCODE_FILE_REQUEST = 1010  # Not used
    ZZ_MQTT_CMD_ALLOW_FIRMWARE_UPDATE = 1011  # Not used
    ZZ_MQTT_CMD_GCODE_FILE_DOWNLOAD = 1020  # Not used
    ZZ_MQTT_CMD_Z_AXIS_RECOUP = 1021  # Not used
    ZZ_MQTT_CMD_EXTRUSION_STEP = 1022  # Not used
    ZZ_MQTT_CMD_ENTER_OR_QUIT_MATERIEL = 1023  # Not used
    ZZ_MQTT_CMD_MOVE_STEP = 1024  # Not used
    ZZ_MQTT_CMD_MOVE_DIRECTION = 1025  # Not used
    ZZ_MQTT_CMD_MOVE_ZERO = 1026  # Not used
    ZZ_MQTT_CMD_APP_QUERY_STATUS = 1027  # Not used
    ZZ_MQTT_CMD_ONLINE_NOTIFY = 1028  # Not used
    ZZ_MQTT_CMD_APP_RECOVER_FACTORY = 1029  # Not used
    ZZ_MQTT_CMD_BLE_ONOFF = 1031  # Not used
    ZZ_MQTT_CMD_DELETE_GCODE_FILE = 1032  # Not used
    ZZ_MQTT_CMD_RESET_GCODE_PARAM = 1032  # Not used
    ZZ_MQTT_CMD_DEVICE_NAME_SET = 1034  # Not used
    ZZ_MQTT_CMD_DEVICE_LOG_UPLOAD = 1035  # Not used
    ZZ_MQTT_CMD_ONOFF_MODAL = 1036  # Not used
    ZZ_MQTT_CMD_MOTOR_LOCK = 1037  # Not used
    ZZ_MQTT_CMD_PREHEAT_CONFIG = 1038  # Not used
    ZZ_MQTT_CMD_BREAK_POINT = 1039  # Not used
    ZZ_MQTT_CMD_AI_CALIB = 1040  # Not used
    ZZ_MQTT_CMD_VIDEO_ONOFF = 1041  # Not used
    ZZ_MQTT_CMD_ADVANCED_PARAMETERS = 1042  # Not used
    ZZ_MQTT_CMD_GCODE_COMMAND = 1043
    ZZ_MQTT_CMD_PREVIEW_IMAGE_URL = 1044  # Not used
    ZZ_MQTT_CMD_SYSTEM_CHECK = 1049  # Not used
    ZZ_MQTT_CMD_AI_SWITCH = 1050  # Not used
    ZZ_MQTT_CMD_AI_INFO_CHECK = 1051  # Not used
    ZZ_MQTT_CMD_MODEL_LAYER = 1052
    TEMP_MAX_PRINT_SPEED = 1055  # max_print_speed: 500
    UNKNOWN_1081 = 1081  # Not used
    UNKNOWN_1084 = 1084  # Not used
    TEMP_IS_LEVELED = 1072  # isLeveled: 1
    TEMP_ERROR_CODE = 1085  # {'errorCode': '0xFF01030001', 'errorLevel': 'P1', 'ext': '{"curFilamentType":["PLA"]}'}
    TEMP_NOZZLE_TYPE = 1093  # value: 0, nozzle_type: 0
    ZZ_STEST_CMD_GCODE_TRANSPOR = 2018  # Not used
    ZZ_MQTT_CMD_ALEXA_MSG = 3000  # Not used


class AnkerStatus(Enum):
    IDLE = "Idle"
    PRINTING = "Printing"
    PAUSED = "Paused"
    ERROR = "Error"  # Not used (unsure how to tell if there's an error)
    OFFLINE = "Offline"
    PREHEATING = "Preheating"
    FINISHED = "Finished"


# TODO: Split this into its own file / module
class FilamentType(Enum):
    NOT_IMPLEMENTED = "Not yet implemented"
    # ...
    PLA = "PLA"
    ABS = "ABS"
    PETG = "PETG"
    Nylon = "Nylon"
    TPU = "TPU"
    # ... Add more filament types here
    UNKNOWN = "Unknown"


FILAMENT_WEIGHT_175 = {
    # https://bitfab.io/blog/3d-printing-materials-densities/
    FilamentType.PLA.value: 2.98,
    FilamentType.ABS.value: 2.50,
    FilamentType.PETG.value: 3.05,
    FilamentType.Nylon.value: 3.65,
    FilamentType.TPU.value: 2.91,
    # ... Add more filament g/m here
}

RESET_STATES = [AnkerStatus.OFFLINE, AnkerStatus.IDLE]
# TODO: Investigate if there are more nozzle types
NOZZLE_TYPES = {
    "0": "Standard",
}
ERROR_CODES = {
    '0xFF01030001': "Filament Broken",
}


@dataclass
class AnkerData:
    _last_heartbeat: datetime = datetime.now()
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
    print_est_finish_time: datetime = None

    motor_locked: bool = False
    ai_enabled: bool = False

    # TODO: Currently no message for filament type except for error messages (afaik). Could derive from the filename.
    filament: FilamentType = FilamentType.NOT_IMPLEMENTED.value

    filament_used: float = 0

    current_speed: int = 0
    max_speed: int = 500

    current_layer: int = 0
    total_layers: int = 0

    hotend_temp: float = 0
    target_hotend_temp: float = 0
    bed_temp: float = 0
    target_bed_temp: float = 0

    def _reset(self):
        for k, v in self.__class__.__dict__.items():
            if not k.startswith('_') and not callable(v) and not property(v):
                self.__dict__[k] = v

    def _pulse(self):
        self._last_heartbeat = datetime.now()

    @property
    def online(self) -> bool:
        return self.status != AnkerStatus.OFFLINE.value

    @property
    def printing(self) -> bool:
        return self.job_name != ""

    @property
    def filament_weight(self) -> float:
        """Returns the weight of the filament used in grams."""
        # PLA is the default filament type (if the filament type is unknown)
        weight = float(FILAMENT_WEIGHT_175.get(self.filament,
                                               FILAMENT_WEIGHT_175.get(FilamentType.PLA.value))) * self.filament_used
        return weight

    def _new_status_handler(self, new_status: AnkerStatus):
        if new_status == self._old_status:
            return

        if self._old_status == AnkerStatus.ERROR:
            self.error_message = ""
            self.error_level = ""

        if new_status in RESET_STATES:
            self._reset()

        self._old_status = new_status

    @property
    def status(self) -> str:
        status = AnkerStatus.PRINTING

        # Check if the printer is heating up
        is_heating_hotend = self.target_hotend_temp - 5 > self.hotend_temp > 30
        is_heating_bed = self.target_bed_temp - 2 > self.bed_temp > 30

        if self._last_heartbeat < datetime.now() - timedelta(seconds=30):
            status = AnkerStatus.OFFLINE
        elif self.error_message:
            status = AnkerStatus.ERROR
        elif self.paused:
            status = AnkerStatus.PAUSED
        elif not self.progress and (is_heating_hotend or is_heating_bed):
            status = AnkerStatus.PREHEATING
        elif not self.printing:
            status = AnkerStatus.IDLE
        elif self.progress == 100:
            status = AnkerStatus.FINISHED

        self._new_status_handler(status)
        return status.value

    def _new_print_job(self):
        self.print_start_time = datetime.now() - timedelta(seconds=self.elapsed_time)
        self.print_est_finish_time = self.print_start_time + timedelta(seconds=self.total_time)

    def _new_job_handler(self):
        if self.job_name != self._old_job_name:
            self._new_print_job()

    def update(self, websocket_message: dict):
        command_type = websocket_message.get("commandType")
        match command_type:
            case CommandTypes.ZZ_MQTT_CMD_EVENT_NOTIFY.value:
                # If the status is "finished", reset the data
                # (Printer does not seem to send a CMD_EVENT_NOTIFY message until you hit "finish" on the printer)
                # This is a bit inconsistent...
                if self.status == AnkerStatus.FINISHED.value:
                    self._reset()
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SCHEDULE.value:
                # Update the status
                self.job_name = websocket_message.get("name")
                self.image = websocket_message.get("img")

                self.progress = websocket_message.get("progress") / 100
                _elapsed_time = int(websocket_message.get("totalTime"))
                _remaining_time = int(websocket_message.get("time"))
                self.elapsed_time = _elapsed_time
                self.remaining_time = _remaining_time
                self.total_time = _elapsed_time + _remaining_time

                self.ai_enabled = websocket_message.get("aiFlag") == 1

                self.filament_used = websocket_message.get(
                    "filamentUsed") / 1000  # Divide by 1000 to get the correct value

                # Register new print job (only on this event)
                self._new_job_handler()
                self._old_job_name = self.job_name
            case CommandTypes.ZZ_MQTT_CMD_MODEL_LAYER.value:
                self.current_layer = websocket_message.get("real_print_layer")
                self.total_layers = websocket_message.get("total_layer")
            case CommandTypes.ZZ_MQTT_CMD_NOZZLE_TEMP.value:
                self._pulse()  # _pulse goes here since this is a reliable mqtt message that doesn't get spammed too much
                self.hotend_temp = websocket_message.get("currentTemp") / 100  # Divide by 100 to get the correct value
                self.target_hotend_temp = websocket_message.get(
                    "targetTemp") / 100  # Divide by 100 to get the correct value
            case CommandTypes.ZZ_MQTT_CMD_FAN_SPEED.value:
                self.fan_speed = websocket_message.get("value")
            case CommandTypes.ZZ_MQTT_CMD_MOTOR_LOCK.value:
                self.motor_locked = websocket_message.get("lock") == 1
            case CommandTypes.ZZ_MQTT_CMD_HOTBED_TEMP.value:
                self.bed_temp = websocket_message.get("currentTemp") / 100  # Divide by 100 to get the correct value
                self.target_bed_temp = websocket_message.get(
                    "targetTemp") / 100  # Divide by 100 to get the correct value
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SPEED.value:
                self.current_speed = websocket_message.get("value")
            case CommandTypes.ZZ_MQTT_CMD_PRINT_CONTROL.value:
                self.paused = not self.paused  # Toggle the paused state (No relevant data in the message :/)
            case CommandTypes.TEMP_MAX_PRINT_SPEED.value:
                self.max_speed = websocket_message.get("max_print_speed")
            case CommandTypes.TEMP_NOZZLE_TYPE.value:
                self.nozzle_type = NOZZLE_TYPES.get(str(websocket_message.get("nozzle_type")),
                                                    str(websocket_message.get("nozzle_type")))
            case CommandTypes.TEMP_IS_LEVELED.value:
                self.bed_leveled = websocket_message.get("isLeveled") == 1
            # Errors (?)
            case CommandTypes.TEMP_ERROR_CODE.value:
                self.error_level = websocket_message.get("errorLevel")
                self.error_message = ERROR_CODES.get(websocket_message.get("errorCode"),
                                                     websocket_message.get("errorCode"))
                if self.error_message not in ERROR_CODES.values():
                    _LOGGER.error(
                        f"Unknown error code: {self.error_message}. Please report this message to the developer with a description of what you were doing when this error occurred. (Received message: {websocket_message})")
            # If the command_type is not handled, raise an exception (unless we know it's not used)
            case _:
                if command_type not in CommandTypes:
                    _LOGGER.error(f"Unknown command_type: {command_type} ({websocket_message})")
                    raise AnkerUnhandledCommandException(f"Unknown command_type: {command_type} ({websocket_message})")
