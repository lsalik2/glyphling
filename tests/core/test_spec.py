import pytest
from asciipet.core.spec import Archetype, Circadian, Species, Body, CreatureSpec

def _sample_spec():
    species = Species(Archetype.BLOB, "omnivore", Circadian.DIURNAL, 1.0, "purr", 1.0)
    body = Body(eyes="o o", mouth="v", ears="^^", pattern="plain", size=2)
    return CreatureSpec(seed=1, name="Moss", species=species, body=body,
                        personality={"bold": 0.2}, quirks=("hums to itself",))

def test_spec_is_value_comparable():
    assert _sample_spec() == _sample_spec()

def test_spec_is_frozen():
    spec = _sample_spec()
    with pytest.raises(Exception):
        spec.name = "Nope"
