from asciipet.session import PetSession
from asciipet.core.events import EventType
from asciipet.core.generator import generate

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
