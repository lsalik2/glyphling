# tests/test_cli_full.py
import asciipet.cli as cli
from asciipet.core.events import EventType

def test_default_state_path_uses_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert cli.default_state_path() == tmp_path / "asciipet" / "pet.json"

def test_rename_command_persists(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    cli.main(["rename", "Pixel"])            # hatches if needed, then renames
    from asciipet.session import PetSession
    import time
    session = PetSession.start(cli.default_state_path(), clock=time.time)
    assert session.spec.name == "Pixel"
