from asciipet.core.simulation import (
    PetState, Mood, NEED_KEYS, new_state, stage_for_age, advance, derive_mood,
)
from asciipet.core.generator import generate
from asciipet.core.events import Event, EventType

SPEC = generate(42)

def test_new_state_defaults():
    s = new_state()
    assert set(s.needs) == set(NEED_KEYS)
    assert all(v == 80.0 for v in s.needs.values())
    assert s.health == 100.0 and s.stage == "egg" and s.asleep is False

def test_stage_for_age():
    assert stage_for_age(0.0) == "egg"
    assert stage_for_age(0.5) == "baby"
    assert stage_for_age(30.0) == "juvenile"
    assert stage_for_age(100.0) == "adult"
    assert stage_for_age(500.0) == "elder"

def test_needs_decay_over_time():
    s = new_state()
    before = s.needs["fullness"]
    advance(s, elapsed_seconds=3600, events=[], spec=SPEC)   # 1 hour
    assert s.needs["fullness"] < before

def test_needs_clamp_at_zero():
    s = new_state()
    advance(s, elapsed_seconds=10_000_000, events=[], spec=SPEC)
    assert all(v >= 0.0 for v in s.needs.values())
