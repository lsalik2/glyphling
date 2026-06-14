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


from glyphling.core import balance

def test_stop_does_not_signal_a_stale_daemon(tmp_path, monkeypatch):
    import glyphling.daemon as d
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=999999, now=1000.0)
    called = []
    monkeypatch.setattr(d.os, "kill", lambda *a: called.append(a))
    d.stop(path, now=1000.0 + balance.DAEMON_STALE_SECONDS + 5)   # stale
    assert called == []                       # never signaled a possibly-reused PID
    assert coord.read_lock(path) is None       # stale lock cleared

def test_status_on_stale_lock_says_not_running(tmp_path, capsys):
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    daemon.print_status(path, now=1000.0 + balance.DAEMON_STALE_SECONDS + 5)  # stale
    assert "not running" in capsys.readouterr().out
