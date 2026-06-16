import colorsys
from glyphling.core.palette import Palette, palette_for, tint

def _sat(rgb):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb))[2]

def _light(rgb):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb))[1]

def _hue(rgb):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb))[0]

def _hue_dist(h, target):
    return abs(((target - h + 0.5) % 1.0) - 0.5)   # shortest arc on the wheel

def test_palette_for_is_deterministic():
    assert palette_for(42) == palette_for(42)
    assert palette_for(42) != palette_for(7)

def test_palette_channels_are_in_a_readable_band():
    for seed in (1, 7, 42, 1000, 99999):
        p = palette_for(seed)
        for rgb in (p.body, p.accent, p.eyes):
            assert len(rgb) == 3 and all(0 <= c <= 255 for c in rgb)
            assert max(rgb) <= 245          # not near-white
            assert min(rgb) >= 40           # not near-black

def test_tint_unknown_mood_is_identity():
    p = palette_for(42)
    assert tint(p, "content") == p

def test_tint_sick_desaturates_body():
    p = palette_for(42)
    assert _sat(tint(p, "sick").body) < _sat(p.body)

def test_tint_sleeping_dims_body():
    p = palette_for(42)
    assert _light(tint(p, "sleeping").body) < _light(p.body)

def test_tint_excited_saturates_body():
    p = palette_for(42)
    assert _sat(tint(p, "excited").body) >= _sat(p.body)

def test_tint_tired_dims_body():
    p = palette_for(42)
    assert _light(tint(p, "tired").body) < _light(p.body)

def test_tint_sad_shifts_hue_toward_blue():
    p = palette_for(42)
    before, after = _hue(p.body), _hue(tint(p, "sad").body)
    assert _hue_dist(after, 0.60) < _hue_dist(before, 0.60)   # closer to blue than before

def test_tint_affects_accent_and_eyes_not_just_body():
    p = palette_for(42)
    t = tint(p, "sick")
    assert t.accent != p.accent and t.eyes != p.eyes
