from dataclasses import dataclass, field
from enum import Enum

class EventType(str, Enum):
    FEED = "feed"
    PLAY = "play"
    CLEAN = "clean"
    REST = "rest"       # toggles sleep; handled specially in advance
    PRAISE = "praise"
    RENAME = "rename"   # changes spec.name; handled by the session, not advance
    # --- Phase 2 sensor events ---
    NIGHTFALL = "nightfall"     # circadian: time to sleep
    MORNING = "morning"         # circadian: time to wake
    CPU_SPIKE = "cpu_spike"     # ambient: machine busy
    LOW_BATTERY = "low_battery" # ambient: low power
    AMBIENT_CLEAR = "ambient_clear"  # ambient: nothing notable
    # --- Phase 3 dev/presence reaction events ---
    TESTS_PASSED = "tests_passed"
    TESTS_FAILED = "tests_failed"
    BUILD_DONE = "build_done"
    BUILD_FAILED = "build_failed"
    COMMITTED = "committed"
    STARTLED = "startled"          # scary command
    WELCOMED_BACK = "welcomed_back" # presence: returned after being away

@dataclass(frozen=True)
class Event:
    type: EventType
    payload: dict = field(default_factory=dict)

# Raw need deltas applied before diminishing-returns/clamping.
EVENT_EFFECTS = {
    EventType.FEED:   {"fullness": 25.0, "happiness": 2.0, "cleanliness": -3.0},
    EventType.PLAY:   {"happiness": 20.0, "social": 10.0, "energy": -15.0, "fullness": -8.0},
    EventType.CLEAN:  {"cleanliness": 35.0},
    EventType.PRAISE: {"social": 15.0, "happiness": 8.0},
}

POSITIVE_BOND_EVENTS = {EventType.PRAISE, EventType.PLAY}

# Deliberate interactions that wake the pet and bump needs/bond.
WAKING_EVENTS = {EventType.FEED, EventType.PLAY, EventType.CLEAN, EventType.PRAISE}

# Ambient sensor events set a transient mood tint (never pump needs, never wake).
AMBIENT_MOOD_EVENTS = {
    EventType.CPU_SPIKE: "excited",
    EventType.LOW_BATTERY: "tired",
    EventType.AMBIENT_CLEAR: "none",
}

def event_to_dict(event: "Event") -> dict:
    return {"type": event.type.value, "payload": event.payload}

def event_from_dict(d: dict) -> "Event":
    return Event(EventType(d["type"]), dict(d.get("payload") or {}))

# Phase 3: dev/presence reaction events (the daemon turns these into a speech bubble + pose).
DEV_REACTION_EVENTS = {
    EventType.TESTS_PASSED, EventType.TESTS_FAILED,
    EventType.BUILD_DONE, EventType.BUILD_FAILED,
    EventType.COMMITTED, EventType.STARTLED, EventType.WELCOMED_BACK,
}

# Reaction events that grant a small bond bump ("wins").
WIN_EVENTS = {
    EventType.TESTS_PASSED, EventType.BUILD_DONE,
    EventType.COMMITTED, EventType.WELCOMED_BACK,
}

# Real user/dev activity used for presence (away-gap) detection.
# Excludes ambient/clock events and the synthesized WELCOMED_BACK.
ACTIVITY_EVENTS = WAKING_EVENTS | {
    EventType.TESTS_PASSED, EventType.TESTS_FAILED,
    EventType.BUILD_DONE, EventType.BUILD_FAILED,
    EventType.COMMITTED, EventType.STARTLED,
}
