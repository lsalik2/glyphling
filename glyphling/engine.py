# glyphling/engine.py
from __future__ import annotations
from dataclasses import replace

from glyphling.core.events import EventType
from glyphling.core.simulation import advance

def apply_events(spec, state, elapsed_seconds: float, events: list):
    """Apply elapsed time + a batch of events. RENAME mutates spec (via replace);
    everything else goes through advance(). Returns (spec, state).
    Used identically by the session (owner mode) and the daemon."""
    sim_events = []
    for ev in events:
        if ev.type == EventType.RENAME:
            spec = replace(spec, name=ev.payload["name"])
        else:
            sim_events.append(ev)
    advance(state, elapsed_seconds, sim_events, spec)
    return spec, state
