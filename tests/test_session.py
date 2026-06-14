from glyphling.session import PetSession
from glyphling.core.events import EventType
from glyphling.core.generator import generate

class FakeClock:
    def __init__(self, t=1000.0): self.t = t
    def __call__(self): return self.t
    def advance(self, dt): self.t += dt

def test_start_hatches_and_persists(tmp_path):
    clock = FakeClock()
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    assert session.spec == generate(7)
    assert (tmp_path / "pet.json").exists()

def test_action_feed_raises_fullness(tmp_path):
    clock = FakeClock()
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    session.state.needs["fullness"] = 10.0
    session.action(EventType.FEED)
    assert session.state.needs["fullness"] > 10.0

def test_tick_advances_time(tmp_path):
    clock = FakeClock()
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    before = session.state.needs["fullness"]
    clock.advance(3600)
    session.tick()
    assert session.state.needs["fullness"] < before

def test_rename_updates_spec_and_persists(tmp_path):
    clock = FakeClock()
    path = tmp_path / "pet.json"
    session = PetSession.start(path, clock=clock, seed=7)
    session.action(EventType.RENAME, {"name": "Pixel"})
    assert session.spec.name == "Pixel"
    reopened = PetSession.start(path, clock=clock)
    assert reopened.spec.name == "Pixel"

def test_render_frame_returns_art(tmp_path):
    clock = FakeClock()
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    art = session.render_frame(0)
    assert isinstance(art, str) and "\n" in art

from glyphling import coord

def test_owner_mode_when_no_daemon_still_advances(tmp_path):
    clock = FakeClock()
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    session.state.needs["fullness"] = 10.0
    session.action(EventType.FEED)
    assert session.state.needs["fullness"] > 10.0

def test_reader_mode_queues_action_instead_of_advancing(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock()
    PetSession.start(path, clock=clock, seed=7)                 # create pet on disk (owner)
    coord.write_heartbeat(path, pid=99999, now=clock())        # pretend a daemon is live
    session = PetSession.start(path, clock=clock, seed=7)
    assert session.reader_mode is True
    fullness_before = session.state.needs["fullness"]
    session.action(EventType.FEED)
    assert [d["type"] for d in coord.drain_events(path)] == ["feed"]
    assert session.state.needs["fullness"] == fullness_before

def test_reader_mode_tick_reloads_disk_state(tmp_path):
    path = tmp_path / "pet.json"
    clock = FakeClock()
    PetSession.start(path, clock=clock, seed=7)
    coord.write_heartbeat(path, pid=99999, now=clock())
    session = PetSession.start(path, clock=clock, seed=7)
    from glyphling import store
    spec, state, _ = store.load(path)
    state.needs["fullness"] = 3.0
    store.save(path, spec, state, now=clock())
    session.tick()
    assert session.state.needs["fullness"] == 3.0

def test_render_frame_shows_live_reaction_bubble(tmp_path):
    clock = FakeClock(1000.0)
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    session.state.reaction_text = "yesss!"
    session.state.reaction_mood = "excited"
    session.state.reaction_expires_at = 1005.0            # clock() = 1000 < 1005 -> live
    art = session.render_frame(0)
    assert "( yesss! )" in art

def test_render_frame_hides_expired_reaction(tmp_path):
    clock = FakeClock(1000.0)
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    session.state.reaction_text = "yesss!"
    session.state.reaction_mood = "excited"
    session.state.reaction_expires_at = 999.0             # already expired
    art = session.render_frame(0)
    assert "yesss" not in art

def test_render_frame_no_bubble_while_asleep(tmp_path):
    clock = FakeClock(1000.0)
    session = PetSession.start(tmp_path / "pet.json", clock=clock, seed=7)
    session.state.asleep = True
    session.state.reaction_text = "yesss!"
    session.state.reaction_expires_at = 1005.0
    art = session.render_frame(0)
    assert "yesss" not in art
