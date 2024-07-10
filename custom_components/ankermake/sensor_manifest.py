from homeassistant import const
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass

from .ankermake_mqtt_adapter import AnkerStatus, FilamentType, AnkerData


# Linter is complaining without this class, it is strictly unnecessary
class Description(SensorEntityDescription):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Key must match the attribute in the AnkerData class
BINARY_SENSOR_DESCRIPTIONS = [
    # Motor Locked
    Description(
        key="motor_locked",
        name="Motor Locked",
        icon="mdi:lock",
        device_class=BinarySensorDeviceClass.LOCK,
        entity_registry_enabled_default=False,
    ),
]

BINARY_SENSOR_WITH_ATTR_DESCRIPTIONS = [
    # AI Enabled
    [Description(
        key="ai_enabled",
        name="AI Detection",
        icon="mdi:brain",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,
    ),
        {
            'state': 'ai_enabled',
            'level': 'ai_level',
            'pause_print': 'ai_pause_print',
            'data_collection': 'ai_data_collection',
        }
    ],
    # Filetransfer service
    [Description(
        key="service_filetransfer",
        name="Filetransfer Service",
        icon="mdi:console",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,  # TODO: Enable this when API is in master
    ),
        {
            'state': '%SVC_ONLINE=filetransfer',
            'status': '%SVC_STATE=filetransfer',
            'possible_states': 'api_service_possible_states',
        }
    ],
    # PPPPservice
    [Description(
        key="service_pppp",
        name="PPPP Service",
        icon="mdi:console",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,  # TODO: Enable this when API is in master
    ),
        {
            'state': '%SVC_ONLINE=pppp',
            'status': '%SVC_STATE=pppp',
            'possible_states': 'api_service_possible_states',
        }
    ],
    # Videoqueue
    [Description(
        key="service_videoqueue",
        name="Videoqueue Service",
        icon="mdi:console",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,  # TODO: Enable this when API is in master
    ),
        {
            'state': '%SVC_ONLINE=videoqueue',
            'status': '%SVC_STATE=videoqueue',
            'possible_states': 'api_service_possible_states',
        }
    ],
    # mqtt
    [Description(
        key="service_mqtt",
        name="MQTT Service",
        icon="mdi:console",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,  # TODO: Enable this when API is in master
    ),
        {
            'state': '%SVC_ONLINE=mqttqueue',
            'status': '%SVC_STATE=mqttqueue',
            'possible_states': 'api_service_possible_states',
        }
    ],
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
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    # Target Time
    Description(
        key="print_target_time",
        name="Target Time",
        icon="mdi:timer-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
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
    # Filament Density
    Description(
        key="filament_density",
        name="Filament Density",
        icon="mdi:weight",
        native_unit_of_measurement="m³",
        entity_registry_enabled_default=False,
    ),
    # Current Speed
    Description(
        key="current_speed",
        name="Speed",
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
        name="Layer",
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
# = denotes a static value ('unit': '=mm/s' would set the unit to mm/s, instead of using an attribute from ankerdata)
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
            'error_level': 'error_level',
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
            'target_time': 'print_target_time',
            'current_speed': 'current_speed',
            'max_speed': 'max_speed',
            'speed_unit': '=mm/s',
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
            'filament_used_unit': '=m',
            'filament_weight': 'filament_weight',
            'filament_weight_unit': '=g',
            'filament_density': 'filament_density',
            'filament_density_unit': '=m³',
        }
    ],
    # Error Message
    [Description(
        key="error",
        name="Error",
        icon="mdi:alert",
        entity_registry_enabled_default=False,
    ),
        {
            'state': 'error_message',
            'error_level': 'error_level',
        }
    ],
]
