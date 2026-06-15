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

class BoomSensor:
    def poll(self, now, spec, state): raise RuntimeError("sensor blew up")

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

def test_tick_once_isolates_a_throwing_sensor(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    clock.advance(3600)
    # A sensor that raises must be skipped, not crash the tick; healthy sensors still apply.
    daemon.tick_once(path, clock, sensors=[BoomSensor(), StubSensor([Event(EventType.NIGHTFALL)])])
    _, state, last_tick = store.load(path)
    assert last_tick == clock()        # the tick completed and persisted
    assert state.asleep is True        # the healthy sensor's NIGHTFALL still applied

def test_tick_once_clamps_catchup(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    clock.advance(10**9)
    daemon.tick_once(path, clock, sensors=[])
    _, state, _ = store.load(path)
    assert state.health >= 5.0

from glyphling.sensors.shell import ShellSensor
from glyphling.core import balance

def test_default_sensors_includes_shell(tmp_path):
    sensors = daemon.default_sensors(tmp_path / "pet.json")
    assert any(isinstance(s, ShellSensor) for s in sensors)

def test_tick_once_stamps_reaction_and_bumps_bond_on_commit(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    store.save(path, generate(7), new_state(), now=clock())
    log = tmp_path / "shell-events.log"
    sensor = ShellSensor(path)
    log.write_text("0\tgit commit -m x\n")
    daemon.tick_once(path, clock, sensors=[sensor])       # first poll primes -> discards
    _, s1, _ = store.load(path)
    assert s1.reaction_text == ""                          # backlog discarded, no reaction
    bond0 = s1.bond
    log.write_text("0\tgit commit -m y\n")
    clock.advance(10)
    daemon.tick_once(path, clock, sensors=[sensor])       # now reacts
    _, s2, _ = store.load(path)
    assert s2.reaction_text != "" and s2.reaction_mood == "excited"
    assert s2.reaction_expires_at == clock() + balance.REACTION_TTL
    assert s2.bond > bond0                                  # commit is a "win"

def test_tick_once_welcomes_back_after_away_gap(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(100000.0)
    store.save(path, generate(7), new_state(), now=clock())
    sensor = ShellSensor(path)
    log = tmp_path / "shell-events.log"
    log.write_text("0\tls\n")
    daemon.tick_once(path, clock, sensors=[sensor])        # prime
    spec, st, _ = store.load(path)
    st.last_active_at = clock() - balance.AWAY_THRESHOLD_SECONDS - 100
    store.save(path, spec, st, now=clock())
    log.write_text("0\tgit commit -m back\n")
    daemon.tick_once(path, clock, sensors=[sensor])
    _, st2, _ = store.load(path)
    assert st2.reaction_mood == "happy"                    # welcome-back greeting won (appended last)
    assert st2.reaction_text != ""
    assert st2.last_active_at == clock()

def test_tick_once_no_reaction_while_asleep(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock(1000.0)
    spec, st = generate(7), new_state()
    st.asleep, st.sleep_reason = True, "circadian"
    store.save(path, spec, st, now=clock())
    sensor = ShellSensor(path)
    (tmp_path / "shell-events.log").write_text("0\tgit commit -m x\n")
    daemon.tick_once(path, clock, sensors=[sensor])        # prime
    (tmp_path / "shell-events.log").write_text("0\tgit commit -m y\n")
    daemon.tick_once(path, clock, sensors=[sensor])
    _, st2, _ = store.load(path)
    assert st2.reaction_text == "" and st2.bond == 0.0     # asleep -> no bubble, no bond
