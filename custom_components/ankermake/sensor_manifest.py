from homeassistant import const
from homeassistant.components.sensor import SensorEntityDescription


class Description(SensorEntityDescription):
    def __init__(self, *args, **kwargs):
        # Linter is complaining without this...
        super().__init__(*args, **kwargs)


BINARY_SENSOR_DESCRIPTIONS = []  # Unused in favor of SENSOR_WITH_ATTR_DESCRIPTIONS
"""[
    # AI Enabled
    Description(
        key="ai_enabled",
        name="AI Detection Enabled",
        icon="mdi:brain",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,
    ),
]"""

SENSOR_DESCRIPTIONS = []  # Unused in favor of SENSOR_WITH_ATTR_DESCRIPTIONS
"""[
    # Status
    Description(
        key="status",
        name="Status",
        icon="mdi:printer-3d",
    ),
    # Job Name
    Description(
        key="job_name",
        name="Job Name",
        icon="mdi:file-document",
    ),
    # Gcode Preview URL (Image)
    Description(
        key="image",
        name="Gcode Preview URL",
        icon="mdi:image",
    ),
    # Progress
    Description(
        key="progress",
        name="Progress",
        icon="mdi:progress-wrench",
        native_unit_of_measurement=const.PERCENTAGE,
    ),
    # Elapsed Time
    Description(
        key="elapsed_time",
        name="Elapsed Time",
        icon="mdi:timer-outline",
        native_unit_of_measurement=const.UnitOfTime.SECONDS,
    ),
    # Remaining Time
    Description(
        key="remaining_time",
        name="Remaining Time",
        icon="mdi:timer-sand",
        native_unit_of_measurement=const.UnitOfTime.SECONDS,
    ),
    # Total Time
    Description(
        key="total_time",
        name="Total Time",
        icon="mdi:timer",
        native_unit_of_measurement=const.UnitOfTime.SECONDS,
    ),
    # Filament Used
    Description(
        key="filament_used",
        name="Filament Used",
        icon="mdi:pipe",
        native_unit_of_measurement="mm",
    ),
    # Current Speed
    Description(
        key="current_speed",
        name="Current Speed",
        icon="mdi:speedometer",
        native_unit_of_measurement="mm/s",
    ),
    # Current Layer
    Description(
        key="current_layer",
        name="Current Layer",
        icon="mdi:layers-triple",
    ),
    # Total Layers
    Description(
        key="total_layers",
        name="Total Layers",
        icon="mdi:layers-triple",
    ),
    # Hotend Temp
    Description(
        key="hotend_temp",
        name="Hotend Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
    # Target Hotend Temp
    Description(
        key="target_hotend_temp",
        name="Target Hotend Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
    # Bed Temp
    Description(
        key="bed_temp",
        name="Bed Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
    # Target Bed Temp
    Description(
        key="target_bed_temp",
        name="Target Bed Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
]"""

SENSOR_WITH_ATTR_DESCRIPTIONS = [
    # 3D Printer Sensor
    [Description(
        key="3d_printer",
        name="3D Printer",
        icon="mdi:printer-3d",
    ),
        {
            'state': 'status',
            'ai_enabled': 'ai_enabled',
            'possible_states': 'possible_states',
        }
    ],
    # Hotend Sensor
    [Description(
        key="hotend",
        name="Hotend",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
        {
            'state': 'hotend_temp',
            'target_temp': 'target_hotend_temp',
        }
    ],
    # Bed Sensor
    [Description(
        key="bed",
        name="Bed",
        icon="mdi:thermometer",
        native_unit_of_measurement=const.UnitOfTemperature.CELSIUS,
    ),
        {
            'state': 'bed_temp',
            'target_temp': 'target_bed_temp',
        }
    ],
    # Print job
    [Description(
        key="print_job",
        name="Print Job",
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
            'filament_used': 'filament_used',
            'start_time': 'print_start_time',
            'estimated_finish_time': 'print_est_finish_time',
            'filament_unit': 'filament_unit',
            'current_speed': 'current_speed',
            'current_layer': 'current_layer',
            'total_layers': 'total_layers',
        }
    ]
]
