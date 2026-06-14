# tests/sensors/test_clock.py
from glyphling.sensors.clock import should_sleep, ClockSensor
from glyphling.core.events import EventType
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state

def test_should_sleep_diurnal():
    assert should_sleep("diurnal", 3) is True
    assert should_sleep("diurnal", 12) is False

def test_should_sleep_nocturnal_is_inverted():
    assert should_sleep("nocturnal", 12) is True
    assert should_sleep("nocturnal", 3) is False

def test_should_sleep_crepuscular_naps_midday():
    assert should_sleep("crepuscular", 13) is True
    assert should_sleep("crepuscular", 8) is False

def _spec(circadian):
    s = generate(7)
    from dataclasses import replace
    return replace(s, species=replace(s.species, circadian=type(s.species.circadian)(circadian)))

def test_clock_emits_nightfall_when_awake_at_night():
    spec = _spec("diurnal")
    state = new_state()
    sensor = ClockSensor(hour_fn=lambda now: 2)
    events = sensor.poll(now=0.0, spec=spec, state=state)
    assert [e.type for e in events] == [EventType.NIGHTFALL]

def test_clock_emits_morning_only_for_circadian_sleeper():
    spec = _spec("diurnal")
    state = new_state()
    state.asleep, state.sleep_reason = True, "circadian"
    sensor = ClockSensor(hour_fn=lambda now: 12)
    assert [e.type for e in sensor.poll(0.0, spec, state)] == [EventType.MORNING]
    state.sleep_reason = "manual"
    assert sensor.poll(0.0, spec, state) == []

def test_clock_quiet_when_already_in_the_right_state():
    spec = _spec("diurnal")
    state = new_state()
    sensor = ClockSensor(hour_fn=lambda now: 12)
    assert sensor.poll(0.0, spec, state) == []
