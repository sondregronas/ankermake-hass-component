import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent) + '\\custom_components')

from custom_components.ankermake.ankermake_mqtt_adapter import AnkerData, FilamentType


def test_filament_from_name():
    # Assume the LAST filament type in the name is the correct one
    a = AnkerData()
    a.job_name = 'PLA_HOLDER_PETG_M5.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.PETG.value

    a.job_name = 'Playground_Part_1.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.UNKNOWN.value

    a.job_name = 'PETG_HOLDER_M5.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.PETG.value

    a.job_name = 'NYLON_PETG_PLA_ABS.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.ABS.value

    a.job_name = 'pla.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.PLA.value

    a.job_name = 'pla+.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.PLA.value

    a.job_name = 'notpla.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.UNKNOWN.value

    a.job_name = 'nYlOn.gcode'
    a._new_print_job()
    assert a.filament == FilamentType.NYLON.value
