from dataclasses import dataclass
from enum import Enum


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
    UNKNOWN_1081 = 1081  # Not used
    UNKNOWN_1084 = 1084  # Not used
    ZZ_STEST_CMD_GCODE_TRANSPOR = 2018  # Not used
    ZZ_MQTT_CMD_ALEXA_MSG = 3000  # Not used


@dataclass
class AnkerData:
    printing: bool = False

    job_name: str = "Unknown"
    image: str = ""

    progress: int = 0
    elapsed_time: int = 0
    remaining_time: int = 0
    total_time: int = 0

    ai_enabled: bool = False

    filament_used: int = 0
    filament_unit: str = "mm"

    current_speed: int = 0

    current_layer: int = 0
    total_layers: int = 0

    hotend_temp: float = 0
    target_hotend_temp: float = 0
    bed_temp: float = 0
    target_bed_temp: float = 0

    def update(self, websocket_message: dict):
        command_type = websocket_message.get("commandType")
        match command_type:
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SCHEDULE.value:
                # Update the status
                self.job_name = websocket_message.get("name")
                self.printing = self.job_name != ""
                self.image = websocket_message.get("img")

                self.progress = websocket_message.get("progress") / 100
                _elapsed_time = int(websocket_message.get("totalTime"))
                _remaining_time = int(websocket_message.get("time"))
                self.elapsed_time = _elapsed_time
                self.remaining_time = _remaining_time
                self.total_time = _elapsed_time + _remaining_time

                self.ai_enabled = websocket_message.get("aiFlag") == 1

                self.filament_used = websocket_message.get("filamentUsed")
                self.filament_unit = websocket_message.get("filamentUnit")
            case CommandTypes.ZZ_MQTT_CMD_MODEL_LAYER.value:
                self.current_layer = websocket_message.get("real_print_layer")
                self.total_layers = websocket_message.get("total_layer")
            case CommandTypes.ZZ_MQTT_CMD_NOZZLE_TEMP.value:
                self.hotend_temp = websocket_message.get("currentTemp") / 100
                self.target_hotend_temp = websocket_message.get("targetTemp") / 100
            case CommandTypes.ZZ_MQTT_CMD_HOTBED_TEMP.value:
                self.bed_temp = websocket_message.get("currentTemp") / 100
                self.target_bed_temp = websocket_message.get("targetTemp") / 100
            case CommandTypes.ZZ_MQTT_CMD_PRINT_SPEED.value:
                self.current_speed = websocket_message.get("speed")

            # If the command_type is not handled, raise an exception (unless we know it's not used)
            case _:
                if command_type not in CommandTypes:
                    raise AnkerUnhandledCommandException(f"Unknown command_type: {command_type} ({websocket_message})")
