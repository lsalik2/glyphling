# tests/tui/test_app.py
import pytest
from asciipet.session import PetSession
from asciipet.tui.app import AsciiPetApp

class FakeClock:
    def __init__(self, t=1000.0): self.t = t
    def __call__(self): return self.t

@pytest.mark.asyncio
async def test_feed_key_increases_fullness(tmp_path):
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    session.state.needs["fullness"] = 20.0
    app = AsciiPetApp(session)
    async with app.run_test() as pilot:
        await pilot.press("f")
    assert session.state.needs["fullness"] > 20.0

@pytest.mark.asyncio
async def test_widgets_present(tmp_path):
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    app = AsciiPetApp(session)
    async with app.run_test():
        assert app.query_one("#pet") is not None
        assert app.query_one("#stats") is not None
