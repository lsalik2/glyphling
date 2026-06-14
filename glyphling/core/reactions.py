# glyphling/core/reactions.py
"""Pure mapping from a dev/presence event to a personality-flavored speech line + pose.
No I/O, no clock. The daemon supplies a rotating `salt` for variety; the TUI renders it."""
from glyphling.core.events import EventType

# event -> (mood, {tone: [lines]}). Tone is "loud" or "soft", chosen by personality.
_REACTIONS = {
    EventType.TESTS_PASSED: ("excited", {
        "loud": ["all green!", "yesss!", "nailed it!"],
        "soft": ["all green.", "nice, passing.", "good — green."],
    }),
    EventType.BUILD_DONE: ("excited", {
        "loud": ["built it!", "it compiles!", "ship it!"],
        "soft": ["built.", "phew, done.", "compiled."],
    }),
    EventType.COMMITTED: ("excited", {
        "loud": ["yesss!", "shipped it!", "committed!"],
        "soft": ["committed.", "saved it.", "nice commit."],
    }),
    EventType.TESTS_FAILED: ("sad", {
        "loud": ["oof...", "aw, red.", "we'll get it!"],
        "soft": ["oof.", "next time.", "hmm, red."],
    }),
    EventType.BUILD_FAILED: ("sad", {
        "loud": ["aw, the build...", "broke it?", "we'll fix it!"],
        "soft": ["build failed.", "hmm.", "rough one."],
    }),
    EventType.STARTLED: ("startled", {
        "loud": ["whoa!", "careful!", "yikes!"],
        "soft": ["whoa.", "careful.", "eep."],
    }),
    EventType.WELCOMED_BACK: ("happy", {
        "loud": ["you're back!", "missed you!", "hi again!"],
        "soft": ["you're back.", "missed you.", "hey, you."],
    }),
}

def _tone(spec) -> str:
    p = spec.personality
    return "loud" if (p.get("bold", 0.0) + p.get("energy", 0.0)) >= 0.0 else "soft"

def reaction_for(event_type, spec, salt: int = 0):
    """Return (speech_line, mood) for a reaction event, or None if the event has no reaction."""
    entry = _REACTIONS.get(event_type)
    if entry is None:
        return None
    mood, tones = entry
    lines = tones[_tone(spec)]
    return lines[salt % len(lines)], mood
