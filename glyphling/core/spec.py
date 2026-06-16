from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from glyphling.core.palette import Palette, palette_for

class Archetype(str, Enum):
    BLOB = "blob"
    CRITTER = "critter"

class Circadian(str, Enum):
    DIURNAL = "diurnal"
    NOCTURNAL = "nocturnal"
    CREPUSCULAR = "crepuscular"

@dataclass(frozen=True)
class Species:
    archetype: Archetype
    diet: str
    circadian: Circadian
    metabolism: float
    vocab: str
    aging_rate: float

@dataclass(frozen=True)
class Body:
    eyes: str
    mouth: str
    ears: str
    pattern: str
    size: int

@dataclass(frozen=True)
class CreatureSpec:
    seed: int
    name: str
    species: Species
    body: Body
    personality: dict   # axis -> float in [-1, 1]
    quirks: tuple        # tuple[str, ...]
    palette: Palette = None   # seed-derived; filled by __post_init__, never persisted

    def __post_init__(self):
        if self.palette is None:
            object.__setattr__(self, "palette", palette_for(self.seed))
