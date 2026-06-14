from dataclasses import dataclass, field
from enum import Enum

class EventType(str, Enum):
    FEED = "feed"
    PLAY = "play"
    CLEAN = "clean"
    REST = "rest"       # toggles sleep; handled specially in advance
    PRAISE = "praise"
    RENAME = "rename"   # changes spec.name; handled by the session, not advance

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
