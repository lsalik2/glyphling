import dataclasses
import json
import random
import shutil
from pathlib import Path

from glyphling.core.spec import Archetype, Circadian, Species, Body, CreatureSpec
from glyphling.core.simulation import PetState, advance, new_state
from glyphling.core.generator import generate
from glyphling.core import balance

def spec_to_dict(spec: CreatureSpec) -> dict:
    return {
        "seed": spec.seed,
        "name": spec.name,
        "species": {
            "archetype": spec.species.archetype.value,
            "diet": spec.species.diet,
            "circadian": spec.species.circadian.value,
            "metabolism": spec.species.metabolism,
            "vocab": spec.species.vocab,
            "aging_rate": spec.species.aging_rate,
        },
        "body": dataclasses.asdict(spec.body),
        "personality": spec.personality,
        "quirks": list(spec.quirks),
    }

def spec_from_dict(d: dict) -> CreatureSpec:
    sp = d["species"]
    species = Species(
        archetype=Archetype(sp["archetype"]),
        diet=sp["diet"],
        circadian=Circadian(sp["circadian"]),
        metabolism=sp["metabolism"],
        vocab=sp["vocab"],
        aging_rate=sp["aging_rate"],
    )
    body = Body(**d["body"])
    return CreatureSpec(
        seed=d["seed"], name=d["name"], species=species, body=body,
        personality=dict(d["personality"]), quirks=tuple(d["quirks"]),
    )

def save(path, spec: CreatureSpec, state: PetState, now: float) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))
    data = {"spec": spec_to_dict(spec), "state": dataclasses.asdict(state), "last_tick": now}
    path.write_text(json.dumps(data, indent=2))

def load(path):
    data = json.loads(Path(path).read_text())
    return spec_from_dict(data["spec"]), PetState(**data["state"]), data["last_tick"]

def load_or_hatch(path, now: float, seed: int | None = None):
    path = Path(path)
    if path.exists():
        spec, state, last_tick = load(path)
        elapsed = min(max(0.0, now - last_tick), balance.CATCHUP_MAX_SECONDS)
        advance(state, elapsed, [], spec)
        save(path, spec, state, now)
        return spec, state
    chosen = seed if seed is not None else random.randrange(1 << 31)
    spec = generate(chosen)
    state = new_state()
    save(path, spec, state, now)
    return spec, state
