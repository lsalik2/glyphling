import random
from glyphling.core.spec import Archetype, Circadian, Species, Body, CreatureSpec
from glyphling.core import parts

def _make_name(rng: random.Random) -> str:
    name = rng.choice(parts.NAME_ONSETS) + rng.choice(parts.NAME_VOWELS) + rng.choice(parts.NAME_CODAS)
    return name.capitalize()

def generate(seed: int) -> CreatureSpec:
    rng = random.Random(seed)
    species = Species(
        archetype=rng.choice([Archetype.BLOB, Archetype.CRITTER]),
        diet=rng.choice(["herbivore", "carnivore", "omnivore"]),
        circadian=rng.choice(list(Circadian)),
        metabolism=round(rng.uniform(0.8, 1.2), 2),
        vocab=rng.choice(["chirp", "purr", "warble", "click"]),
        aging_rate=round(rng.uniform(0.8, 1.2), 2),
    )
    body = Body(
        eyes=rng.choice(parts.EYE_VARIANTS),
        mouth=rng.choice(parts.MOUTH_VARIANTS),
        ears=rng.choice(parts.EARS_VARIANTS),
        pattern=rng.choice(parts.PATTERN_VARIANTS),
        size=rng.randint(1, 3),
    )
    personality = {axis: round(rng.uniform(-1.0, 1.0), 2) for axis in parts.PERSONALITY_AXES}
    quirks = tuple(rng.sample(parts.QUIRK_POOL, k=2))
    name = _make_name(rng)
    return CreatureSpec(seed=seed, name=name, species=species, body=body,
                        personality=personality, quirks=quirks)
