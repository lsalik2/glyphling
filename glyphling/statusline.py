# glyphling/statusline.py
"""A one-line, read-only glance at the pet for tmux/prompt/`watch`. Pure formatter."""
from glyphling.core import balance
from glyphling.core.simulation import NEED_KEYS

_LABELS = {"fullness": "food", "energy": "enr", "happiness": "hap",
           "cleanliness": "cln", "social": "soc"}


def _bar(value: float, width: int = 4) -> str:
    filled = int(round(max(0.0, min(100.0, value)) / 100 * width))
    return "#" * filled + "-" * (width - filled)


def format_line(spec, state, compact: bool = False) -> str:
    tier = balance.bond_tier(state.bond)
    if compact:
        return f"{spec.name} · {state.mood} · bond: {tier}"
    gauges = " ".join(f"{_LABELS[k]}{_bar(state.needs[k])}" for k in NEED_KEYS)
    return f"{spec.name}  {state.mood}   {gauges}   bond: {tier}"
