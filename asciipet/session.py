from __future__ import annotations
from dataclasses import replace
from pathlib import Path

from asciipet import store
from asciipet.core.events import Event, EventType
from asciipet.core.renderer import render
from asciipet.core.simulation import advance

class PetSession:
    """Controller that ties the pure core to disk via an injectable clock."""

    def __init__(self, path, clock):
        self.path = Path(path)
        self.clock = clock          # callable -> epoch seconds
        self.spec = None
        self.state = None
        self._last = None

    @classmethod
    def start(cls, path, clock, seed: int | None = None) -> "PetSession":
        session = cls(path, clock)
        session.spec, session.state = store.load_or_hatch(path, clock(), seed)
        session._last = clock()
        return session

    def _elapsed(self) -> float:
        now = self.clock()
        dt = max(0.0, now - self._last)
        self._last = now
        return dt

    def tick(self) -> None:
        advance(self.state, self._elapsed(), [], self.spec)
        store.save(self.path, self.spec, self.state, self.clock())

    def action(self, event_type: EventType, payload: dict | None = None) -> None:
        if event_type == EventType.RENAME:
            self.spec = replace(self.spec, name=(payload or {})["name"])
        else:
            advance(self.state, self._elapsed(), [Event(event_type, payload or {})], self.spec)
        store.save(self.path, self.spec, self.state, self.clock())

    def render_frame(self, frame_idx: int = 0) -> str:
        return render(self.spec, self.state.mood, frame_idx)
