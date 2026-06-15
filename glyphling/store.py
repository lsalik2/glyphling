import dataclasses
import json
import os
import random
from pathlib import Path

from glyphling import coord
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
    """Persist atomically: write a temp file, rotate the live file to `.bak`, then
    os.replace the temp into place. A crash mid-save never leaves a partial pet.json,
    and the previous good state survives in `.bak` for recovery."""
    path = Path(path)
    coord.ensure_dir(path.parent)
    data = {"spec": spec_to_dict(spec), "state": dataclasses.asdict(state), "last_tick": now}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    coord.harden_file(tmp)              # published file (and the .bak it rotates into) stays 0600
    if path.exists():
        os.replace(path, path.with_name(path.name + ".bak"))   # keep last-good as .bak
    os.replace(tmp, path)                                       # atomic publish

def _read(path) -> tuple:
    data = json.loads(Path(path).read_text())
    return spec_from_dict(data["spec"]), PetState(**data["state"]), data["last_tick"]

def load(path):
    """Load the pet, falling back to `.bak` if the live file is missing or corrupt
    (a partial write, or the sub-millisecond window mid-save). Raises only if neither
    the live file nor its backup yields valid state."""
    path = Path(path)
    try:
        return _read(path)
    except (OSError, ValueError, KeyError, TypeError):
        bak = path.with_name(path.name + ".bak")
        if bak.exists():
            return _read(bak)
        raise

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
