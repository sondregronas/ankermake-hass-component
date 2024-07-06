from homeassistant import const
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription

from .ankermake_mqtt_adapter import AnkerStatus, FilamentType


# Linter is complaining without this class, it is strictly unnecessary
class Description(SensorEntityDescription):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Key must match the attribute in the AnkerData class
BINARY_SENSOR_DESCRIPTIONS = [
    # AI Enabled
    Description(
        key="ai_enabled",
        name="AI Detection Enabled",
        icon="mdi:brain",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,
    ),
    # Motor Locked
    Description(
        key="motor_locked",
        name="Motor Locked",
        icon="mdi:lock",
        device_class=BinarySensorDeviceClass.LOCK,
        entity_registry_enabled_default=False,
    ),
]

# Key must match the attribute in the AnkerData class
SENSOR_DESCRIPTIONS = [
    # Job Name
    Description(
        key="job_name",
        name="Job Name",
        icon="mdi:file-document",
        entity_registry_enabled_default=False,
    ),
    # Start Time
    Description(
        key="print_start_time",
        name="Start Time",
        icon="mdi:timer-outline",
    ),
    # Estimated Finish Time
    Description(
        key="print_est_finish_time",
        name="Estimated Finish Time",
        icon="mdi:timer-outline",
    ),
    # Filament Used
    Description(
        key="filament_used",
        name="Filament Used",
        icon="mdi:pipe",
        native_unit_of_measurement=const.UnitOfLength.METERS,
        entity_registry_enabled_default=False,
    ),
    # Filament Weight
    Description(
        key="filament_weight",
        name="Filament Weight",
        icon="mdi:weight",
        native_unit_of_measurement=const.UnitOfMass.GRAMS,
        entity_registry_enabled_default=False,
    ),
    # Current Speed
    Description(
        key="current_speed",
        name="Current Speed",
        icon="mdi:speedometer",
        native_unit_of_measurement="mm/s",
        entity_registry_enabled_default=False,
    ),
    # Max Speed
    Description(
        key="max_speed",
        name="Max Speed",
        icon="mdi:speedometer",
        native_unit_of_measurement="mm/s",
        entity_registry_enabled_default=False,
    ),
    # Fan Speed
    Description(
        key="fan_speed",
        name="Fan Speed",
        icon="mdi:fan",
        native_unit_of_measurement=const.PERCENTAGE,
        entity_registry_enabled_default=False,
    ),
    # Current Layer
    Description(
        key="current_layer",
        name="Current Layer",
        icon="mdi:layers-triple",
        entity_registry_enabled_default=False,
    ),
    # Total Layers
    Description(
        key="total_layers",
        name="Total Layers",
        icon="mdi:layers-triple",
        entity_registry_enabled_default=False,
    ),
    # Target Hotend Temp
    Description(
        key="target_hotend_temp",
        name="Target Hotend Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
    # Target Bed Temp
    Description(
        key="target_bed_temp",
        name="Target Bed Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
    ),
]

# Description Key = entity affix
# Dict = {entity_attribute: key_in_ankerdata} (state sets the entity state)
# If one does not intend to use an ankerdata attribute an if statement must be added to the _update_from_anker method
# in sensor.py to prevent an AttributeError (alternatively see _filter_handler method in sensor.py)
SENSOR_WITH_ATTR_DESCRIPTIONS = [
    # 3D Printer Sensor
    [Description(
        key="3d_printer",
        name="3D Printer",
        icon="mdi:printer-3d",
        device_class='enum',
        options=[s.value for s in AnkerStatus],
    ),
        {
            'state': 'status',
            'ai_enabled': 'ai_enabled',
            'motor_locked': 'motor_locked',
            'error_message': 'error_message',
        }
    ],
    # Hotend Sensor
    [Description(
        key="hotend",
        name="Hotend Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
        {
            'state': 'hotend_temp',
            'nozzle_type': 'nozzle_type',
            'target_temp': 'target_hotend_temp',
            'fan_speed': 'fan_speed',
        }
    ],
    # Bed Sensor
    [Description(
        key="bed",
        name="Bed Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
        {
            'state': 'bed_temp',
            'target_temp': 'target_bed_temp',
            'bed_leveled': 'bed_leveled',
        }
    ],
    # Print job
    [Description(
        key="progress",
        name="Progress",
        icon="mdi:file-document",
        native_unit_of_measurement=const.PERCENTAGE,
    ),
        {
            'state': 'progress',
            'gcode_preview_url': 'image',
            'job_name': 'job_name',
            'elapsed_time': '%%TD=elapsed_time',
            'remaining_time': '%%TD=remaining_time',
            'total_print_time': '%%TD=total_time',
            'start_time': 'print_start_time',
            'estimated_finish_time': 'print_est_finish_time',
            'current_speed': 'current_speed',
            'max_speed': 'max_speed',
            'current_layer': 'current_layer',
            'total_layers': 'total_layers',
        }
    ],
    # Filament
    # TODO: Move from print job to filament sensor
    [Description(
        key="filament",
        name="Filament",
        icon="mdi:pipe",
        device_class='enum',
        options=[s.value for s in FilamentType],
    ),
        {
            'state': 'filament',
            'filament_used': 'filament_used',
            'filament_weight': 'filament_weight',
        }
    ],
    # Error Message
    [Description(
        key="error",
        name="Error",
        icon="mdi:alert",
    ),
        {
            'state': 'error_message',
            'error_level': 'error_level',
        }
    ],
]
