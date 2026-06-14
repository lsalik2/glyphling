from glyphling.core.events import EventType, Event, EVENT_EFFECTS, POSITIVE_BOND_EVENTS

def test_user_actions_have_effects_or_special_handling():
    assert EVENT_EFFECTS[EventType.FEED]["fullness"] > 0
    assert EVENT_EFFECTS[EventType.PLAY]["energy"] < 0
    assert EVENT_EFFECTS[EventType.CLEAN]["cleanliness"] > 0
    assert EVENT_EFFECTS[EventType.PRAISE]["social"] > 0

def test_event_defaults_empty_payload():
    assert Event(EventType.FEED).payload == {}

def test_positive_bond_events():
    assert EventType.PRAISE in POSITIVE_BOND_EVENTS
    assert EventType.PLAY in POSITIVE_BOND_EVENTS

from glyphling.core.events import (
    WAKING_EVENTS, AMBIENT_MOOD_EVENTS, event_to_dict, event_from_dict,
)

def test_new_sensor_event_types_exist():
    for name in ("NIGHTFALL", "MORNING", "CPU_SPIKE", "LOW_BATTERY", "AMBIENT_CLEAR"):
        assert hasattr(EventType, name)

def test_waking_events_are_the_deliberate_interactions():
    assert WAKING_EVENTS == {EventType.FEED, EventType.PLAY, EventType.CLEAN, EventType.PRAISE}

def test_ambient_mood_mapping():
    assert AMBIENT_MOOD_EVENTS[EventType.CPU_SPIKE] == "excited"
    assert AMBIENT_MOOD_EVENTS[EventType.LOW_BATTERY] == "tired"
    assert AMBIENT_MOOD_EVENTS[EventType.AMBIENT_CLEAR] == "none"

def test_event_dict_roundtrip():
    ev = Event(EventType.RENAME, {"name": "Pixel"})
    assert event_from_dict(event_to_dict(ev)) == ev
    ev2 = Event(EventType.NIGHTFALL)
    assert event_from_dict(event_to_dict(ev2)) == ev2
