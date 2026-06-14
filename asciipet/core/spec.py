from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

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
