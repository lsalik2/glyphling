# glyphling/core/palette.py
"""Pure, seed-derived creature colors + mood tinting. No I/O and no Rich import — this module
only produces (r, g, b) tuples. The renderer turns them into color markup; the display layer
(Textual/Rich) renders or degrades them."""
import colorsys
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    body: tuple    # (r, g, b), each 0–255
    accent: tuple
    eyes: tuple


def _to_hls(rgb: tuple):
    r, g, b = (c / 255 for c in rgb)
    return colorsys.rgb_to_hls(r, g, b)            # returns (h, l, s)


def _from_hls(h: float, l: float, s: float) -> tuple:
    l = max(0.0, min(1.0, l))
    s = max(0.0, min(1.0, s))
    r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)   # colorsys uses H, L, S order
    return (round(r * 255), round(g * 255), round(b * 255))


def palette_for(seed: int) -> Palette:
    """Deterministic per-creature palette from an RNG stream decorrelated from the generator's.
    Saturation/lightness stay in a readable mid-band so every seed is legible on light or dark."""
    rng = random.Random(seed ^ 0x9E3779B9)
    h = rng.random()
    return Palette(
        body=_from_hls(h, 0.62, 0.45),
        accent=_from_hls(h + 150 / 360, 0.60, 0.50),   # near-complementary
        eyes=_from_hls(h + 0.5, 0.70, 0.70),           # bright contrast
    )


# mood -> transform applied to each color in HLS space. (Tinted palettes may push a channel
# slightly past palette_for's readable band — still valid 0–255 and renders fine.)
_BLUE_SHIFT = {"sat": 0.75, "light": 0.95, "toward": 0.60, "pull": 0.30}   # toward blue hue
_TINT = {
    "sick":     {"sat": 0.35, "light": 0.95, "toward": 0.30, "pull": 0.45},   # sickly green
    "sad":      _BLUE_SHIFT,
    "lonely":   _BLUE_SHIFT,
    "tired":    {"sat": 0.75, "light": 0.80, "toward": None, "pull": 0.0},     # dim + muted
    "sleeping": {"sat": 0.80, "light": 0.65, "toward": None, "pull": 0.0},     # dim + muted
    "happy":    {"sat": 1.20, "light": 1.08, "toward": None, "pull": 0.0},
    "excited":  {"sat": 1.25, "light": 1.10, "toward": None, "pull": 0.0},
    "playful":  {"sat": 1.20, "light": 1.08, "toward": None, "pull": 0.0},
}


def _tint_color(rgb: tuple, rule: dict) -> tuple:
    h, l, s = _to_hls(rgb)
    s *= rule["sat"]
    l *= rule["light"]
    if rule["toward"] is not None:
        diff = ((rule["toward"] - h + 0.5) % 1.0) - 0.5   # shortest hue arc
        h = h + diff * rule["pull"]
    return _from_hls(h, l, s)


def tint(palette: Palette, mood: str) -> Palette:
    """Return a mood-tinted copy of the palette (identity for moods with no rule)."""
    rule = _TINT.get(mood)
    if rule is None:
        return palette
    return Palette(
        body=_tint_color(palette.body, rule),
        accent=_tint_color(palette.accent, rule),
        eyes=_tint_color(palette.eyes, rule),
    )
