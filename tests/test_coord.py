# tests/test_coord.py
import os
import stat
import sys

import pytest

from glyphling import coord
from glyphling.core import balance

def test_heartbeat_and_liveness(tmp_path):
    path = tmp_path / "pet.json"
    assert coord.is_daemon_alive(path, now=1000.0) is False
    coord.write_heartbeat(path, pid=4321, now=1000.0)
    assert coord.is_daemon_alive(path, now=1000.0) is True
    lock = coord.read_lock(path)
    assert lock["pid"] == 4321
    assert coord.is_daemon_alive(path, now=1000.0 + balance.DAEMON_STALE_SECONDS + 1) is False

def test_clear_lock(tmp_path):
    path = tmp_path / "pet.json"
    coord.write_heartbeat(path, pid=1, now=1.0)
    coord.clear_lock(path)
    assert coord.read_lock(path) is None

def test_event_queue_append_and_drain(tmp_path):
    path = tmp_path / "pet.json"
    assert coord.drain_events(path) == []
    coord.append_event(path, {"type": "feed", "payload": {}})
    coord.append_event(path, {"type": "rename", "payload": {"name": "Pixel"}})
    drained = coord.drain_events(path)
    assert [d["type"] for d in drained] == ["feed", "rename"]
    assert coord.drain_events(path) == []

def test_drain_tolerates_garbage_lines(tmp_path):
    path = tmp_path / "pet.json"
    coord.append_event(path, {"type": "feed", "payload": {}})
    (tmp_path / "events.jsonl").open("a").write("not json\n")
    drained = coord.drain_events(path)
    assert [d["type"] for d in drained] == ["feed"]

def test_drain_lines_claims_and_clears(tmp_path):
    log = tmp_path / "x.log"
    log.write_text("a\nb\n")
    assert coord.drain_lines(log) == ["a", "b"]
    assert not log.exists()                 # the log was claimed and removed
    assert coord.drain_lines(log) == []     # nothing left to drain

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file permissions only")
def test_coord_files_and_dir_are_user_only(tmp_path):
    d = tmp_path / "glyphling"
    path = d / "pet.json"
    coord.append_event(path, {"type": "feed", "payload": {}})   # event queue holds your actions
    coord.write_heartbeat(path, pid=1, now=1.0)
    assert stat.S_IMODE(os.stat(d / "events.jsonl").st_mode) == 0o600
    assert stat.S_IMODE(os.stat(d / "daemon.lock").st_mode) == 0o600
    assert stat.S_IMODE(os.stat(d).st_mode) == 0o700
