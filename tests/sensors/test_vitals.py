# tests/sensors/test_vitals.py
from glyphling.sensors.vitals import VitalsSensor
from glyphling.core.events import EventType
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state

SPEC = generate(7)

def _sensor(cpu, battery, charging):
    return VitalsSensor(reader=lambda: (cpu, battery, charging))

def test_high_cpu_emits_spike():
    ev = _sensor(95.0, 80.0, True).poll(0.0, SPEC, new_state())
    assert [e.type for e in ev] == [EventType.CPU_SPIKE]

def test_low_unplugged_battery_emits_low_battery_and_wins_over_cpu():
    ev = _sensor(95.0, 10.0, False).poll(0.0, SPEC, new_state())
    assert [e.type for e in ev] == [EventType.LOW_BATTERY]

def test_low_battery_while_charging_is_not_low():
    ev = _sensor(10.0, 10.0, True).poll(0.0, SPEC, new_state())
    assert [e.type for e in ev] == [EventType.AMBIENT_CLEAR]

def test_normal_emits_ambient_clear():
    ev = _sensor(10.0, 90.0, False).poll(0.0, SPEC, new_state())
    assert [e.type for e in ev] == [EventType.AMBIENT_CLEAR]

def test_missing_battery_is_tolerated():
    ev = _sensor(10.0, None, False).poll(0.0, SPEC, new_state())
    assert [e.type for e in ev] == [EventType.AMBIENT_CLEAR]
