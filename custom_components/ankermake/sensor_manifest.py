from homeassistant import const
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription


class Description(SensorEntityDescription):
    def __init__(self, *args, **kwargs):
        # Linter is complaining without this...
        super().__init__(*args, **kwargs)


BINARY_SENSOR_DESCRIPTIONS = [
    # Printing
    Description(
        key="printing",
        name="Printing",
        icon="mdi:printer-3d",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    # AI Enabled
    Description(
        key="ai_enabled",
        name="AI Detection",
        icon="mdi:brain",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
]

SENSOR_DESCRIPTIONS = [
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
        name="Bed Temperture",
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
]
