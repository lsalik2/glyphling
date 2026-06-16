from glyphling.core.generator import generate
from glyphling.core.spec import Archetype
from glyphling.core import parts

def test_same_seed_is_deterministic():
    assert generate(12345) == generate(12345)

def test_different_seeds_differ():
    assert generate(1) != generate(2)

def test_generated_parts_are_valid():
    spec = generate(777)
    assert spec.species.archetype in list(Archetype)
    assert spec.body.eyes in parts.EYE_VARIANTS
    assert spec.body.mouth in parts.MOUTH_VARIANTS
    assert set(spec.personality) == set(parts.PERSONALITY_AXES)
    assert all(-1.0 <= v <= 1.0 for v in spec.personality.values())
    assert len(spec.quirks) == 2 and len(set(spec.quirks)) == 2
    assert spec.name and spec.name[0].isupper()


def test_minimal_drift_preserves_identity():
    # Adding archetypes must NOT change name/diet/circadian/vocab/metabolism/quirks for a seed.
    from glyphling.core.generator import generate
    g42 = generate(42)
    assert g42.name == "Boox"
    assert g42.species.diet == "herbivore" and g42.species.circadian.value == "crepuscular"
    assert g42.species.vocab == "purr" and g42.species.metabolism == 0.91
    assert g42.quirks == ("sneezes when startled", "collects pebbles")
    g7 = generate(7)
    assert g7.name == "Meess"
    assert g7.species.diet == "herbivore" and g7.species.circadian.value == "nocturnal"
    assert g7.species.vocab == "chirp" and g7.species.metabolism == 1.06
    assert g7.quirks == ("sleeps upside-down", "sneezes when startled")

def test_generate_is_deterministic_including_archetype():
    from glyphling.core.generator import generate
    assert generate(42) == generate(42)
    assert generate(123).species.archetype == generate(123).species.archetype

def test_all_six_archetypes_are_reachable():
    from glyphling.core.generator import generate
    seen = {generate(s).species.archetype.value for s in range(300)}
    assert seen == {"blob", "critter", "avian", "serpentine", "quadruped", "tuft"}
