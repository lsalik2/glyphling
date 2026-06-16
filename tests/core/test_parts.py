from glyphling.core import parts

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

def test_template_for_egg_is_shared():
    from glyphling.core import parts
    assert parts.template_for("blob", "egg") == parts.EGG_TEMPLATE
    assert parts.template_for("critter", "egg") == parts.EGG_TEMPLATE

def test_template_for_adult_matches_body_templates():
    from glyphling.core import parts
    for a in ("blob", "critter"):
        assert parts.template_for(a, "adult") == parts.BODY_TEMPLATES[a]

def test_template_for_unknown_stage_falls_back_to_adult():
    from glyphling.core import parts
    assert parts.template_for("blob", "wat") == parts.BODY_TEMPLATES["blob"]

def test_baby_is_shorter_than_adult():
    from glyphling.core import parts
    for a in ("blob", "critter"):
        assert len(parts.template_for(a, "baby")) < len(parts.template_for(a, "adult"))

def test_new_archetypes_have_all_stages():
    from glyphling.core import parts
    for a in ("avian", "serpentine", "quadruped", "tuft"):
        for stage in ("baby", "juvenile", "adult", "elder"):
            t = parts.template_for(a, stage)
            assert isinstance(t, list) and len(t) >= 2
        assert parts.template_for(a, "egg") == parts.EGG_TEMPLATE          # egg shared
        assert len(parts.template_for(a, "baby")) < len(parts.template_for(a, "adult"))
