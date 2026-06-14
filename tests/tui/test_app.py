# tests/tui/test_app.py
import pytest
from glyphling.session import PetSession
from glyphling.tui.app import GlyphlingApp

class FakeClock:
    def __init__(self, t=1000.0): self.t = t
    def __call__(self): return self.t

@pytest.mark.asyncio
async def test_feed_key_increases_fullness(tmp_path):
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    session.state.needs["fullness"] = 20.0
    app = GlyphlingApp(session)
    async with app.run_test() as pilot:
        await pilot.press("f")
    assert session.state.needs["fullness"] > 20.0

@pytest.mark.asyncio
async def test_widgets_present(tmp_path):
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    app = GlyphlingApp(session)
    async with app.run_test():
        assert app.query_one("#pet") is not None
        assert app.query_one("#stats") is not None

@pytest.mark.asyncio
async def test_name_with_markup_renders_literally(tmp_path):
    import dataclasses
    from textual.widgets import Static
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    session.spec = dataclasses.replace(session.spec, name="[red]Boom[/]")
    app = GlyphlingApp(session)
    async with app.run_test() as pilot:
        await pilot.pause()
        stats = app.query_one("#stats", Static)
        content = str(stats.visual)
        assert "[red]Boom[/]" in content   # literal brackets preserved, not interpreted

@pytest.mark.asyncio
async def test_animation_interval_does_not_crash(tmp_path):
    session = PetSession.start(tmp_path / "pet.json", clock=FakeClock(), seed=7)
    app = GlyphlingApp(session)
    async with app.run_test() as pilot:
        await pilot.pause(0.3)        # let the 0.25s animation interval fire
        assert app._exception is None  # no callback raised
