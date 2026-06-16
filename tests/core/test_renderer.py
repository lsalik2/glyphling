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

def test_upside_down_sleep_pose():
    import dataclasses
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    upside = dataclasses.replace(generate(7), quirks=("sleeps upside-down", "hums to itself"))
    assert "v v" in render(upside, "sleeping", frame_idx=0)        # inverted eyes
    plain = dataclasses.replace(generate(7), quirks=("hums to itself", "collects pebbles"))
    assert "v v" not in render(plain, "sleeping", frame_idx=0)

def test_render_without_palette_is_plain_no_markup():
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    art = render(generate(42), "content", frame_idx=0)
    assert "[" not in art and "]" not in art      # plain text, no Rich markup

def test_render_with_palette_emits_body_color_markup():
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    from glyphling.core.palette import palette_for
    p = palette_for(42)
    art = render(generate(42), "content", frame_idx=0, speech="hi!", palette=p)
    body = f"rgb({p.body[0]},{p.body[1]},{p.body[2]})"
    assert body in art                              # body color applied
    assert f"rgb({p.eyes[0]},{p.eyes[1]},{p.eyes[2]})" in art   # eyes color applied
    assert "( hi! )" in art                         # bubble text still present (wrapped)

def test_colored_markup_parses_to_exact_plain_art_for_all_archetypes():
    # Rich must parse the color markup back to EXACTLY the plain art — guards the critter
    # trailing-backslash case (seed 7 is a critter: template lines end with '\').
    from rich.text import Text
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    from glyphling.core.palette import palette_for
    assert {generate(42).species.archetype.value, generate(7).species.archetype.value} == {"blob", "critter"}
    for seed in (42, 7):
        spec = generate(seed)
        for mood in ("content", "sleeping"):
            colored = render(spec, mood, frame_idx=0, speech="hi!", palette=palette_for(seed))
            plain = render(spec, mood, frame_idx=0, speech="hi!")
            assert Text.from_markup(colored).plain == plain

def test_render_stage_default_adult_is_unchanged():
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    spec = generate(42)
    assert render(spec, "content", frame_idx=0) == render(spec, "content", frame_idx=0, stage="adult")

def test_render_baby_is_shorter_than_adult():
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    spec = generate(42)
    baby = render(spec, "content", frame_idx=0, stage="baby")
    adult = render(spec, "content", frame_idx=0, stage="adult")
    assert baby.count("\n") < adult.count("\n")

def test_render_egg_has_no_face_substitution_error():
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    art = render(generate(42), "content", frame_idx=0, stage="egg")
    assert ".-." in art

def test_color_round_trips_for_all_stages_and_archetypes():
    from rich.text import Text
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    from glyphling.core.palette import palette_for, tint
    for seed in (42, 7):                                # blob, critter
        spec = generate(seed)
        for stage in ("egg", "baby", "juvenile", "adult", "elder"):
            for mood in ("content", "sleeping"):
                c = render(spec, mood, 0, speech="hi!", stage=stage, palette=tint(palette_for(seed), mood))
                p = render(spec, mood, 0, speech="hi!", stage=stage)
                assert Text.from_markup(c).plain == p

def test_color_round_trips_for_every_archetype():
    import dataclasses
    from rich.text import Text
    from glyphling.core.generator import generate
    from glyphling.core.renderer import render
    from glyphling.core.palette import palette_for, tint
    from glyphling.core.spec import Archetype
    base = generate(42)
    for arch in Archetype:
        spec = dataclasses.replace(base, species=dataclasses.replace(base.species, archetype=arch))
        for stage in ("egg", "baby", "juvenile", "adult", "elder"):
            for mood in ("content", "sleeping"):
                c = render(spec, mood, 0, speech="hi", stage=stage, palette=tint(palette_for(42), mood))
                p = render(spec, mood, 0, speech="hi", stage=stage)
                assert Text.from_markup(c).plain == p, f"{arch.value}/{stage}/{mood}"
