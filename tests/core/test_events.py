from asciipet.core.events import EventType, Event, EVENT_EFFECTS, POSITIVE_BOND_EVENTS

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
