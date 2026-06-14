# tests/test_engine.py
from glyphling.engine import apply_events
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state
from glyphling.core.events import Event, EventType

SPEC = generate(7)

def test_rename_updates_spec_not_via_advance():
    spec, state = generate(7), new_state()
    spec, state = apply_events(spec, state, 0, [Event(EventType.RENAME, {"name": "Pixel"})])
    assert spec.name == "Pixel"

def test_non_rename_events_and_elapsed_go_through_advance():
    spec, state = generate(7), new_state()
    state.needs["fullness"] = 10.0
    spec, state = apply_events(spec, state, 0, [Event(EventType.FEED)])
    assert state.needs["fullness"] > 10.0

def test_decay_applied_once_for_batch():
    spec, state = generate(7), new_state()
    before = state.needs["fullness"]
    spec, state = apply_events(spec, state, 3600, [])
    assert state.needs["fullness"] < before
