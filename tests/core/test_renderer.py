from asciipet.core.generator import generate
from asciipet.core.renderer import render

def test_render_uses_base_face_when_content():
    spec = generate(42)
    art = render(spec, "content", frame_idx=0)
    assert spec.body.eyes in art          # not blinking on frame 0
    assert spec.body.mouth in art

def test_mood_overrides_face():
    spec = generate(42)
    art = render(spec, "tired", frame_idx=0)
    assert "- -" in art                    # tired eyes override

def test_blink_on_fourth_frame():
    spec = generate(42)
    assert "- -" in render(spec, "content", frame_idx=3)

def test_sleeping_shows_z():
    spec = generate(42)
    art = render(spec, "sleeping", frame_idx=0)
    assert "z" in art.lower()

def test_render_is_deterministic():
    spec = generate(42)
    assert render(spec, "content", 1) == render(spec, "content", 1)
