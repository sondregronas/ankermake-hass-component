from enum import Enum


class AnkerException(BaseException):
    ...


class AnkerUnhandledCommandException(AnkerException):
    ...


class AnkerStatus(Enum):
    IDLE = "Idle"
    PRINTING = "Printing"
    PAUSED = "Paused"
    ERROR = "Error"
    OFFLINE = "Offline"
    PREHEATING = "Preheating"
    FINISHED = "Finished"


# AnkerMake MQTT Command Types (ankermake-m5-research/ankerctl)
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
    TEMP_PRINT_STOPPED = 1068  # {'name': 'name', 'img': 'url', 'totalTime': 0, 'filamentUsed': 0, 'filamentUnit': 'mm', 'saveTime': 0, 'trigger': 2})
    UNKNOWN_1081 = 1081  # Not used
    UNKNOWN_1084 = 1084  # Not used
    TEMP_IS_LEVELED = 1072  # isLeveled: 1
    TEMP_ERROR_CODE = 1085  # {'errorCode': '0xFF01030001', 'errorLevel': 'P1', 'ext': '{"curFilamentType":["PLA"]}'}
    TEMP_NOZZLE_TYPE = 1093  # value: 0, nozzle_type: 0
    ZZ_STEST_CMD_GCODE_TRANSPOR = 2018  # Not used
    ZZ_MQTT_CMD_ALEXA_MSG = 3000  # Not used


class FilamentType(Enum):
    # ...
    PLA = "PLA"
    ABS = "ABS"
    PETG = "PETG"
    NYLON = "Nylon"
    TPU = "TPU"
    # -- These are probably not relevant or probably won't be detected on their own, but here they are --
    PC = "PC"
    WOOD = "Wood"
    CARBONFIBER = "CF"
    # PCA_ABS = "PCAABS"
    HIPS = "HIPS"
    PVA = "PVA"
    ASA = "ASA"
    POLYPROPYLENE = "PP"
    ACETAL = "POM"
    PMMA = "PMMA"
    FPE = "FPE"
    # ... Add more filament types here
    UNKNOWN = "Unknown"

    @staticmethod
    def options_regex() -> str:
        return f'({"|".join([f.value for f in FilamentType if f.value not in [FilamentType.UNKNOWN.value]])})'

    @staticmethod
    def upper_dict() -> dict[str, str]:
        return {f.value.upper(): f.value for f in FilamentType}


FILAMENT_WEIGHT_175 = {
    # https://bitfab.io/blog/3d-printing-materials-densities/
    FilamentType.PLA.value: 2.98,
    FilamentType.ABS.value: 2.50,
    FilamentType.PETG.value: 3.05,
    FilamentType.NYLON.value: 3.65,
    FilamentType.TPU.value: 2.91,
    # ---
    FilamentType.PC.value: 3.13,
    FilamentType.WOOD.value: 3.08,
    FilamentType.CARBONFIBER.value: 3.13,
    # FilamentType.PCA_ABS.value: 2.86,
    FilamentType.HIPS.value: 2.48,
    FilamentType.PVA.value: 2.96,
    FilamentType.ASA.value: 2.52,
    FilamentType.POLYPROPYLENE.value: 2.16,
    FilamentType.ACETAL.value: 3.37,
    FilamentType.PMMA.value: 2.84,
    FilamentType.FPE.value: 5.19,
    # ... Add more filament g/m here
}

FILAMENT_DENSITY = {
    # g/cm^3
    # https://bitfab.io/blog/3d-printing-materials-densities/
    FilamentType.PLA.value: 1.24,
    FilamentType.ABS.value: 1.04,
    FilamentType.PETG.value: 1.27,
    FilamentType.NYLON.value: 1.52,
    FilamentType.TPU.value: 1.21,
    # ---
    FilamentType.PC.value: 1.3,
    FilamentType.WOOD.value: 1.28,
    FilamentType.CARBONFIBER.value: 1.3,
    # FilamentType.PCA_ABS.value: 1.19,
    FilamentType.HIPS.value: 1.03,
    FilamentType.PVA.value: 1.23,
    FilamentType.ASA.value: 1.05,
    FilamentType.POLYPROPYLENE.value: 0.9,
    FilamentType.ACETAL.value: 1.4,
    FilamentType.PMMA.value: 1.18,
    FilamentType.FPE.value: 2.16,
}

# TODO: Investigate if there are more nozzle types
NOZZLE_TYPES = {
    '0': 'Standard',
}
ERROR_CODES = {
    '0xFF01030001': 'Filament Broken',  # P1 The filament is broken. Please replace the filament and try again.
    '0xFF01030005': 'Failed to transfer Gcode, please try again.',  # As shown in the app.
}

# TODO: This is just a guess, these are not used anywhere!!
ERROR_LEVELS = {
    'P0': 'INFO',  # Before printing / something to do with gcode
    'P1': 'ERROR',  # During printing / something to do with filament
    # 'P2': 'CRITICAL',  # Just a guess, haven't seen P2 yet
}
