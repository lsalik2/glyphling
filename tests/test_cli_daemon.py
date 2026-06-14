# tests/test_cli_daemon.py
import glyphling.cli as cli
from glyphling import daemon, coord

def test_status_reports_not_running(tmp_path, capsys):
    path = tmp_path / "pet.json"
    daemon.print_status(path, now=1000.0)
    assert "not running" in capsys.readouterr().out

def test_status_reports_running(tmp_path, capsys):
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    daemon.print_status(path, now=1000.0)
    out = capsys.readouterr().out
    assert "running" in out and "4321" in out

def test_stop_clears_a_stale_lock(tmp_path):
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=2147480000, now=1000.0)   # pid almost certainly not alive
    daemon.stop(path, now=1000.0)
    assert coord.read_lock(path) is None

def test_cli_daemon_status_dispatch(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    cli.main(["daemon", "status"])
    assert "not running" in capsys.readouterr().out
