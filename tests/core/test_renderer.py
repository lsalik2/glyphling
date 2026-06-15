from glyphling.core.generator import generate
from glyphling.core.renderer import render

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

def test_startled_face_renders():
    spec = generate(42)
    art = render(spec, "startled", frame_idx=0)
    assert "O O" in art          # startled wide eyes

def test_speech_bubble_renders_above_the_pet():
    spec = generate(42)
    art = render(spec, "excited", frame_idx=0, speech="yesss!")
    assert "( yesss! )" in art
    assert art.splitlines()[0].strip() == "( yesss! )"

def test_no_speech_means_no_bubble():
    spec = generate(42)
    art = render(spec, "content", frame_idx=0)
    assert "yesss" not in art

def test_speech_line_is_reserved_so_the_body_never_shifts():
    spec = generate(42)
    with_speech = render(spec, "excited", frame_idx=0, speech="hi!").splitlines()
    without = render(spec, "content", frame_idx=0).splitlines()
    assert len(with_speech) == len(without)      # bubble pops in place, no layout shift
    assert with_speech[0].strip() == "( hi! )"
    assert without[0].strip() == ""              # top line reserved, blank when silent
