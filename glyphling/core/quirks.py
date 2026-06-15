# glyphling/core/quirks.py
"""Pure, deterministic mapping from a creature's quirks to behavior: occasional idle speech
bubbles, event-triggered flourishes, and a sleeping-pose tweak. No I/O, no clock — `now` and a
`salt` are injected. Surfaces through the existing reaction transient."""
from glyphling.core import balance
from glyphling.core.events import EventType

# Real activity the "headbangs to fast typing" quirk reacts to.
DEV_ACTIVITY_EVENTS = {
    EventType.TESTS_PASSED, EventType.TESTS_FAILED,
    EventType.BUILD_DONE, EventType.BUILD_FAILED, EventType.COMMITTED,
}

# quirk name -> behavior. kind: "idle" | "event" | "pose".
QUIRKS = {
    "chases its tail":          {"kind": "idle",  "mood": "playful",
                                 "lines": ["*chases its tail*", "round and round!", "...almost got it"]},
    "hums to itself":           {"kind": "idle",  "mood": "playful",
                                 "lines": ["hmm-hm-hmm", "*humming*", "la la la"]},
    "collects pebbles":         {"kind": "idle",  "mood": "playful",
                                 "lines": ["ooh, a pebble!", "*pockets a pebble*", "shiny rock!"]},
    "sneezes when startled":    {"kind": "event", "on": "STARTLED", "mood": "startled",
                                 "lines": ["*achoo!*", "hh-CHOO!", "*sneeze*"]},
    "headbangs to fast typing": {"kind": "event", "on": "DEV_ACTIVITY", "mood": "excited",
                                 "lines": ["*headbang*", "boom boom boom", "rock on"]},
    "sleeps upside-down":       {"kind": "pose",  "pose": "upside_down"},
}


def _hash(*ints) -> int:
    """Deterministic 32-bit hash of ints (Python's hash() is salted for str, stable for int)."""
    h = 2166136261
    for n in ints:
        h = (h * 16777619 + (int(n) & 0xFFFFFFFF)) & 0xFFFFFFFF
    return h


def has_pose_quirk(spec, pose: str) -> bool:
    return any(QUIRKS.get(q, {}).get("pose") == pose for q in spec.quirks)


def _idle_pool(spec) -> list:
    return [q for q in spec.quirks if QUIRKS.get(q, {}).get("kind") == "idle"]


def idle_quirk(spec, bond: float, now: float):
    """Return (line, mood) for an idle quirk bubble, or None. Fires at most once per 'fire bucket'.
    As bond rises the bucket shrinks (more frequent), quiet buckets thin out, and the pet's favorite
    quirk is weighted up — so a bonded pet often does its favorite thing. Deterministic in
    (spec.seed, bond, now)."""
    pool = _idle_pool(spec)
    if not pool:
        return None
    span = balance.QUIRK_BUCKET_MAX_SECONDS - balance.QUIRK_BUCKET_MIN_SECONDS
    clamped = min(max(bond, 0.0), balance.BOND_MAX)
    bucket = balance.QUIRK_BUCKET_MAX_SECONDS - span * clamped / balance.BOND_MAX
    idx = int(now // bucket)
    if now - idx * bucket >= balance.QUIRK_FIRE_WINDOW_SECONDS:
        return None
    tier = balance.tier_index(bond)
    silence = max(0, balance.QUIRK_SILENCE_SLOTS - tier)   # fewer quiet buckets as bond rises
    favorite = pool[spec.seed % len(pool)]
    slots = pool + [favorite] * tier + [None] * silence    # favorite weighted up by tier
    choice = slots[_hash(idx, spec.seed) % len(slots)]
    if choice is None:                                     # a quiet bucket
        return None
    lines = QUIRKS[choice]["lines"]
    return lines[_hash(idx, spec.seed, 1) % len(lines)], QUIRKS[choice]["mood"]


def event_quirk(spec, event_type, salt: int = 0):
    """Return (line, mood) if the pet has an event quirk matching event_type, else None."""
    for q in spec.quirks:
        e = QUIRKS.get(q, {})
        if e.get("kind") != "event":
            continue
        on = e["on"]
        if (on == "STARTLED" and event_type == EventType.STARTLED) or \
           (on == "DEV_ACTIVITY" and event_type in DEV_ACTIVITY_EVENTS):
            lines = e["lines"]
            return lines[salt % len(lines)], e["mood"]
    return None
