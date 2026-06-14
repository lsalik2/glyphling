from asciipet.core import parts

def test_every_archetype_has_a_template():
    for archetype in ("blob", "critter"):
        assert archetype in parts.BODY_TEMPLATES
        assert any("{eyes}" in line for line in parts.BODY_TEMPLATES[archetype])
        assert any("{mouth}" in line for line in parts.BODY_TEMPLATES[archetype])

def test_variant_lists_non_empty():
    for lst in (parts.EYE_VARIANTS, parts.MOUTH_VARIANTS, parts.EARS_VARIANTS,
                parts.PATTERN_VARIANTS, parts.QUIRK_POOL):
        assert len(lst) >= 2

def test_mood_face_covers_all_moods():
    expected = {"content","happy","excited","playful","hungry","tired",
                "lonely","grumpy","sad","sick","sleeping"}
    assert expected <= set(parts.MOOD_FACE)
