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

def test_stop_does_not_kill_a_recycled_pid(tmp_path, monkeypatch):
    # Fresh heartbeat, but the PID now belongs to some unrelated (recycled) process.
    import glyphling.daemon as d
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    killed = []
    monkeypatch.setattr(d.os, "kill", lambda *a: killed.append(a))
    monkeypatch.setattr(d, "_pid_is_glyphling_daemon", lambda pid: False, raising=False)
    d.stop(path, now=1000.0)
    assert killed == []                    # refused to signal a process that isn't our daemon
    assert coord.read_lock(path) is None   # cleared the bogus lock instead

def test_stop_signals_a_verified_live_daemon(tmp_path, monkeypatch):
    import glyphling.daemon as d
    import signal as _signal
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    killed = []
    monkeypatch.setattr(d.os, "kill", lambda pid, sig: killed.append((pid, sig)))
    monkeypatch.setattr(d, "_pid_is_glyphling_daemon", lambda pid: True, raising=False)
    d.stop(path, now=1000.0)
    assert killed == [(4321, _signal.SIGTERM)]   # verified our daemon -> signaled it

def test_status_on_stale_lock_says_not_running(tmp_path, capsys):
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    daemon.print_status(path, now=1000.0 + balance.DAEMON_STALE_SECONDS + 5)  # stale
    assert "not running" in capsys.readouterr().out

def test_start_ensures_state_dir_before_forking(tmp_path, monkeypatch, capsys):
    """Regression: `glyphling daemon start` on a fresh XDG dir must create the state dir
    (so the child's daemon.log open can't fail). We monkeypatch os.fork to take the parent
    path WITHOUT actually forking a child."""
    import glyphling.daemon as d
    path = tmp_path / "glyphling" / "pet.json"     # parent dir does NOT exist yet
    monkeypatch.setattr(d.os, "fork", lambda: 4242)  # pretend we're the parent
    d.start(path)
    assert path.parent.exists()                     # start ensured the state dir exists
    assert "started" in capsys.readouterr().out
