# tests/test_daemon_integration.py
import subprocess
import sys
import time
from glyphling import store, coord
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state

def test_real_daemon_ticks_then_stops_cleanly(tmp_path):
    path = tmp_path / "pet.json"
    store.save(path, generate(7), new_state(), now=time.time() - 3600)  # 1h stale

    proc = subprocess.Popen(
        [sys.executable, "-m", "glyphling.daemon", "--state", str(path), "--interval", "0.2"]
    )
    try:
        deadline = time.time() + 8.0
        beat = False
        while time.time() < deadline:
            if coord.is_daemon_alive(path, time.time()):
                beat = True
                break
            time.sleep(0.1)
        assert beat, "daemon never wrote a fresh heartbeat"
    finally:
        proc.terminate()
        proc.wait(timeout=8)

    assert (tmp_path / "daemon.lock").exists() is False
