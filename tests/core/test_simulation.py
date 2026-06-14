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

def test_feed_raises_fullness_with_diminishing_returns():
    s = new_state()
    s.needs["fullness"] = 0.0
    advance(s, 0, [Event(EventType.FEED)], SPEC)
    big = s.needs["fullness"]
    s.needs["fullness"] = 90.0
    advance(s, 0, [Event(EventType.FEED)], SPEC)
    small_gain = s.needs["fullness"] - 90.0
    assert big > 20.0          # near-empty feed gives most of +25
    assert small_gain < 5.0    # nearly-full feed gives little

def test_rest_toggles_sleep_and_energy_recovers():
    s = new_state()
    advance(s, 0, [Event(EventType.REST)], SPEC)
    assert s.asleep is True
    s.needs["energy"] = 40.0
    advance(s, 3600, [], SPEC)             # one hour asleep
    assert s.needs["energy"] > 40.0

def test_health_never_below_floor():
    s = new_state()
    for _ in range(50):
        advance(s, 86_400, [], SPEC)       # 50 days of total neglect
    from asciipet.core import balance
    assert s.health >= balance.HEALTH_FLOOR
    assert s.health > 0                     # cannot die

def test_health_regenerates_when_cared_for():
    s = new_state()
    advance(s, 86_400 * 5, [], SPEC)        # neglect -> low health
    low = s.health
    for _ in range(5):                      # top everything up
        for k in NEED_KEYS:
            s.needs[k] = 100.0
        advance(s, 3600, [], SPEC)
    assert s.health > low

def test_praise_raises_bond():
    s = new_state()
    before = s.bond
    advance(s, 0, [Event(EventType.PRAISE)], SPEC)
    assert s.bond > before

def test_mood_sleeping_and_hungry():
    s = new_state()
    advance(s, 0, [Event(EventType.REST)], SPEC)
    assert s.mood == "sleeping"
    s2 = new_state()
    s2.needs["fullness"] = 5.0
    advance(s2, 0, [], SPEC)
    assert s2.mood in ("hungry", "sick")
