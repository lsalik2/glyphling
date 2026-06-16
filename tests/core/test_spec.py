import pytest
from glyphling.core.spec import Archetype, Circadian, Species, Body, CreatureSpec

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

def test_generated_spec_has_seed_derived_palette():
    from glyphling.core.generator import generate
    from glyphling.core.palette import palette_for
    spec = generate(42)
    assert spec.palette == palette_for(42)
    assert generate(42).palette == generate(42).palette

def test_replace_keeps_palette():
    import dataclasses
    from glyphling.core.generator import generate
    spec = generate(42)
    assert dataclasses.replace(spec, name="Pixel").palette == spec.palette

def test_loaded_spec_recomputes_palette(tmp_path):
    from glyphling import store
    from glyphling.core.generator import generate
    from glyphling.core.simulation import new_state
    from glyphling.core.palette import palette_for
    path = tmp_path / "pet.json"
    store.save(path, generate(42), new_state(), now=1.0)
    spec2, _, _ = store.load(path)
    assert spec2.palette == palette_for(42)
