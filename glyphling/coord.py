# glyphling/coord.py
"""File-as-truth coordination: a heartbeat lockfile and an append-only event queue.
Both live beside the state file (pet.json) in the same directory."""
import json
import os
from pathlib import Path

from glyphling.core import balance

def _lock_path(state_path) -> Path:
    return Path(state_path).with_name("daemon.lock")

def _queue_path(state_path) -> Path:
    return Path(state_path).with_name("events.jsonl")

def write_heartbeat(state_path, pid: int, now: float) -> None:
    p = _lock_path(state_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"pid": pid, "heartbeat": now}))

def read_lock(state_path):
    p = _lock_path(state_path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (ValueError, OSError):
        return None

def is_daemon_alive(state_path, now: float) -> bool:
    lock = read_lock(state_path)
    if not lock:
        return False
    return (now - lock.get("heartbeat", 0)) < balance.DAEMON_STALE_SECONDS

def clear_lock(state_path) -> None:
    _lock_path(state_path).unlink(missing_ok=True)

def append_event(state_path, event_dict: dict) -> None:
    q = _queue_path(state_path)
    q.parent.mkdir(parents=True, exist_ok=True)
    with open(q, "a") as f:
        f.write(json.dumps(event_dict) + "\n")

def drain_events(state_path) -> list:
    """Atomically claim the queue (rename), then read it. Appends that race with a
    drain land in a fresh queue file and are picked up next drain."""
    q = _queue_path(state_path)
    if not q.exists():
        return []
    processing = q.with_name(q.name + ".processing")
    try:
        os.replace(q, processing)
    except OSError:
        return []
    out = []
    for line in processing.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    processing.unlink(missing_ok=True)
    return out
