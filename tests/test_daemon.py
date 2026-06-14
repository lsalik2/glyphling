# tests/test_daemon.py
from glyphling import daemon, store, coord
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state
from glyphling.core.events import Event, EventType

class FakeClock:
    def __init__(self, t=1000.0): self.t = t
    def __call__(self): return self.t
    def advance(self, dt): self.t += dt

class StubSensor:
    def __init__(self, events): self._events = events
    def poll(self, now, spec, state): return list(self._events)

def test_tick_once_writes_heartbeat_and_advances(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    clock.advance(3600)
    daemon.tick_once(path, clock, sensors=[])
    assert coord.is_daemon_alive(path, now=clock()) is True
    _, state, last_tick = store.load(path)
    assert last_tick == clock()
    assert state.needs["fullness"] < 80.0

def test_tick_once_drains_queue_and_applies_sensor_events(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    coord.append_event(path, {"type": "feed", "payload": {}})
    daemon.tick_once(path, clock, sensors=[StubSensor([Event(EventType.NIGHTFALL)])])
    _, state, _ = store.load(path)
    assert state.asleep is True
    assert coord.drain_events(path) == []

def test_tick_once_clamps_catchup(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    clock.advance(10**9)
    daemon.tick_once(path, clock, sensors=[])
    _, state, _ = store.load(path)
    assert state.health >= 5.0
