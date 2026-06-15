# glyphling/daemon.py
from __future__ import annotations
import os
import signal
import sys
import time
from pathlib import Path

from glyphling import store, coord
from glyphling.core import balance
from glyphling.core.events import event_from_dict, Event, EventType, ACTIVITY_EVENTS
from glyphling.core.reactions import reaction_for
from glyphling.engine import apply_events

def default_sensors(path):
    from glyphling.sensors.clock import ClockSensor
    from glyphling.sensors.vitals import VitalsSensor
    from glyphling.sensors.shell import ShellSensor
    return [ClockSensor(), VitalsSensor(), ShellSensor(path)]

def tick_once(path, clock, sensors) -> None:
    """One daemon iteration: heartbeat, gather queued + sensor events, apply, stamp the
    transient reaction + presence, persist."""
    now = clock()
    coord.write_heartbeat(path, os.getpid(), now)
    spec, state, last_tick = store.load(path)
    elapsed = min(max(0.0, now - last_tick), balance.CATCHUP_MAX_SECONDS)
    events = [event_from_dict(d) for d in coord.drain_events(path)]
    for sensor in sensors:
        try:
            events.extend(sensor.poll(now, spec, state))
        except Exception as exc:   # sensors are best-effort: a broken one is skipped, never sinks the daemon
            print(f"glyphling: sensor {type(sensor).__name__} failed: {exc!r}", file=sys.stderr)

    # Presence: fresh activity after a long idle gap -> welcome back.
    activity = any(e.type in ACTIVITY_EVENTS for e in events)
    was_away = state.last_active_at > 0 and (now - state.last_active_at) > balance.AWAY_THRESHOLD_SECONDS
    if activity and was_away and not state.asleep:
        events.append(Event(EventType.WELCOMED_BACK))

    spec, state = apply_events(spec, state, elapsed, events)

    if activity:
        state.last_active_at = now

    # Stamp the visible reaction transient: the latest reaction-producing event wins.
    if not state.asleep:
        for ev in reversed(events):
            r = reaction_for(ev.type, spec, salt=int(now))
            if r is not None:
                state.reaction_text, state.reaction_mood = r
                state.reaction_expires_at = now + balance.REACTION_TTL
                break

    store.save(path, spec, state, now)

def run(path, clock=None, interval=None, sensors=None) -> None:
    """Foreground tick loop until SIGTERM/SIGINT. Clears the lock on exit."""
    clock = clock or time.time
    interval = interval if interval is not None else balance.DAEMON_INTERVAL_SECONDS
    sensors = sensors if sensors is not None else default_sensors(path)
    store.load_or_hatch(path, clock())
    flag = {"running": True}
    def _stop(*_a):
        flag["running"] = False
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    try:
        while flag["running"]:
            tick_once(path, clock, sensors)
            time.sleep(interval)
    finally:
        coord.clear_lock(path)

def main(argv=None) -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="glyphling-daemon")
    parser.add_argument("--state", required=True)
    parser.add_argument("--interval", type=float, default=balance.DAEMON_INTERVAL_SECONDS)
    args = parser.parse_args(argv)
    run(Path(args.state), clock=time.time, interval=args.interval)

if __name__ == "__main__":
    main()

def status(path, now) -> bool:
    return coord.is_daemon_alive(path, now)

def print_status(path, now=None) -> None:
    now = time.time() if now is None else now
    lock = coord.read_lock(path)
    if status(path, now) and lock is not None:
        print(f"glyphling daemon running (pid {lock['pid']})")
    else:
        print("glyphling daemon not running")

def stop(path, now=None) -> None:
    now = time.time() if now is None else now
    lock = coord.read_lock(path)
    if not lock:
        print("glyphling daemon not running")
        return
    if not status(path, now):
        coord.clear_lock(path)
        print("glyphling daemon not running (cleared stale lock)")
        return
    try:
        os.kill(lock["pid"], signal.SIGTERM)
        print("stopping glyphling daemon")
    except (ProcessLookupError, PermissionError, OSError):
        coord.clear_lock(path)
        print("glyphling daemon not running (cleared stale lock)")

def start(path, interval=None) -> None:
    if status(path, time.time()):
        print("glyphling daemon already running")
        return
    coord.ensure_dir(Path(path).parent)   # ensure state dir (0700) for log + state
    pid = os.fork()
    if pid > 0:
        print("glyphling daemon started")
        return
    # child: detach from the controlling terminal and run the loop, logging to daemon.log
    os.setsid()
    log_path = Path(path).with_name("daemon.log")
    log = open(log_path, "a")
    coord.harden_file(log_path)
    devnull = os.open(os.devnull, os.O_RDONLY)
    os.dup2(devnull, 0)                    # detach stdin
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    os.close(devnull)
    if log.fileno() > 2:
        log.close()                       # fds 1/2 hold the file open; drop the extra handle
    try:
        run(path, interval=interval)
    finally:
        os._exit(0)
