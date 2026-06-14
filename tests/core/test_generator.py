from glyphling.core.generator import generate
from glyphling.core.spec import Archetype
from glyphling.core import parts

def test_same_seed_is_deterministic():
    assert generate(12345) == generate(12345)

def test_different_seeds_differ():
    assert generate(1) != generate(2)

def test_generated_parts_are_valid():
    spec = generate(777)
    assert spec.species.archetype in (Archetype.BLOB, Archetype.CRITTER)
    assert spec.body.eyes in parts.EYE_VARIANTS
    assert spec.body.mouth in parts.MOUTH_VARIANTS
    assert set(spec.personality) == set(parts.PERSONALITY_AXES)
    assert all(-1.0 <= v <= 1.0 for v in spec.personality.values())
    assert len(spec.quirks) == 2 and len(set(spec.quirks)) == 2
    assert spec.name and spec.name[0].isupper()
