# tests/core/test_reactions.py
from dataclasses import replace
from glyphling.core.reactions import reaction_for
from glyphling.core.events import EventType
from glyphling.core.generator import generate

SPEC = generate(7)

def _with_personality(spec, **axes):
    p = dict(spec.personality); p.update(axes)
    return replace(spec, personality=p)

def test_non_reaction_event_returns_none():
    assert reaction_for(EventType.FEED, SPEC) is None
    assert reaction_for(EventType.CPU_SPIKE, SPEC) is None

def test_each_reaction_event_yields_text_and_mood():
    expected_mood = {
        EventType.TESTS_PASSED: "excited", EventType.BUILD_DONE: "excited",
        EventType.COMMITTED: "excited", EventType.TESTS_FAILED: "sad",
        EventType.BUILD_FAILED: "sad", EventType.STARTLED: "startled",
        EventType.WELCOMED_BACK: "happy",
    }
    for et, mood in expected_mood.items():
        text, m = reaction_for(et, SPEC, salt=0)
        assert isinstance(text, str) and text and m == mood

def test_deterministic_for_same_inputs():
    assert reaction_for(EventType.COMMITTED, SPEC, salt=3) == reaction_for(EventType.COMMITTED, SPEC, salt=3)

def test_salt_varies_the_line():
    s = _with_personality(SPEC, bold=1.0, energy=1.0)
    lines = {reaction_for(EventType.COMMITTED, s, salt=i)[0] for i in range(6)}
    assert len(lines) > 1

def test_personality_changes_tone():
    loud = _with_personality(SPEC, bold=1.0, energy=1.0)
    soft = _with_personality(SPEC, bold=-1.0, energy=-1.0)
    loud_lines = {reaction_for(EventType.COMMITTED, loud, salt=i)[0] for i in range(6)}
    soft_lines = {reaction_for(EventType.COMMITTED, soft, salt=i)[0] for i in range(6)}
    assert loud_lines != soft_lines

def test_welcome_back_warms_with_bond():
    from glyphling.core.reactions import reaction_for
    from glyphling.core.events import EventType
    from glyphling.core.generator import generate
    spec = generate(7)
    stranger = reaction_for(EventType.WELCOMED_BACK, spec, salt=0, bond=0.0)
    bonded = reaction_for(EventType.WELCOMED_BACK, spec, salt=0, bond=100.0)
    assert stranger[1] == "happy" and bonded[1] == "happy"
    assert stranger[0] != bonded[0]            # warmer line at high bond

def test_non_greeting_reaction_ignores_bond():
    from glyphling.core.reactions import reaction_for
    from glyphling.core.events import EventType
    from glyphling.core.generator import generate
    spec = generate(7)
    a = reaction_for(EventType.TESTS_PASSED, spec, salt=0, bond=0.0)
    b = reaction_for(EventType.TESTS_PASSED, spec, salt=0, bond=100.0)
    assert a == b and a is not None
