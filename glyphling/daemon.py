# glyphling/daemon.py
from __future__ import annotations
import os
import signal
import time
from pathlib import Path

from glyphling import store, coord
from glyphling.core import balance
from glyphling.core.events import event_from_dict
from glyphling.engine import apply_events

def default_sensors():
    from glyphling.sensors.clock import ClockSensor
    from glyphling.sensors.vitals import VitalsSensor
    return [ClockSensor(), VitalsSensor()]

def tick_once(path, clock, sensors) -> None:
    """One daemon iteration: heartbeat, gather queued + sensor events, advance, persist."""
    now = clock()
    coord.write_heartbeat(path, os.getpid(), now)
    spec, state, last_tick = store.load(path)
    elapsed = min(max(0.0, now - last_tick), balance.CATCHUP_MAX_SECONDS)
    events = [event_from_dict(d) for d in coord.drain_events(path)]
    for sensor in sensors:
        events.extend(sensor.poll(now, spec, state))
    spec, state = apply_events(spec, state, elapsed, events)
    store.save(path, spec, state, now)

def run(path, clock=None, interval=None, sensors=None) -> None:
    """Foreground tick loop until SIGTERM/SIGINT. Clears the lock on exit."""
    clock = clock or time.time
    interval = interval if interval is not None else balance.DAEMON_INTERVAL_SECONDS
    sensors = sensors if sensors is not None else default_sensors()
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
