# glyphling/session.py
from __future__ import annotations
from pathlib import Path

from glyphling import store, coord
from glyphling.core.events import Event, EventType, event_to_dict
from glyphling.core.renderer import render
from glyphling.core.palette import tint
from glyphling.engine import apply_events

class PetSession:
    """Controller tying the pure core to disk via an injectable clock.

    Owner mode (no live daemon): this session advances the sim and writes state.
    Reader mode (a daemon is live): the daemon owns ticking; this session appends
    user actions to the event queue and polls disk to display the daemon's state.
    """

    def __init__(self, path, clock):
        self.path = Path(path)
        self.clock = clock          # callable -> epoch seconds
        self.spec = None
        self.state = None
        self._last = None

    @classmethod
    def start(cls, path, clock, seed: int | None = None) -> "PetSession":
        session = cls(path, clock)
        now = clock()
        if coord.is_daemon_alive(path, now) and Path(path).exists():
            session.spec, session.state, _ = store.load(path)     # reader: just load
        else:
            session.spec, session.state = store.load_or_hatch(path, now, seed)
        session._last = clock()
        return session

    @property
    def reader_mode(self) -> bool:
        return coord.is_daemon_alive(self.path, self.clock())

    def _elapsed(self) -> float:
        now = self.clock()
        dt = max(0.0, now - self._last)
        self._last = now
        return dt

    def _reload(self) -> None:
        if self.path.exists():
            self.spec, self.state, _ = store.load(self.path)
        self._last = self.clock()

    def tick(self) -> None:
        if self.reader_mode:
            self._reload()
        else:
            self.spec, self.state = apply_events(self.spec, self.state, self._elapsed(), [])
            store.save(self.path, self.spec, self.state, self.clock())

    def action(self, event_type: EventType, payload: dict | None = None) -> None:
        ev = Event(event_type, payload or {})
        if self.reader_mode:
            coord.append_event(self.path, event_to_dict(ev))
            self._reload()
        else:
            self.spec, self.state = apply_events(self.spec, self.state, self._elapsed(), [ev])
            store.save(self.path, self.spec, self.state, self.clock())

    def render_frame(self, frame_idx: int = 0) -> str:
        st = self.state
        if st.reaction_text and not st.asleep and self.clock() < st.reaction_expires_at:
            mood, speech = st.reaction_mood, st.reaction_text
        else:
            mood, speech = st.mood, ""
        return render(self.spec, mood, frame_idx, speech=speech,
                      palette=tint(self.spec.palette, mood), stage=st.stage)
