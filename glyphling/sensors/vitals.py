# glyphling/sensors/vitals.py
from glyphling.core.events import Event, EventType
from glyphling.core import balance

def _psutil_reader():
    import psutil
    cpu = psutil.cpu_percent(interval=None)
    batt = psutil.sensors_battery()
    if batt is None:
        return cpu, None, False
    return cpu, batt.percent, batt.power_plugged

class VitalsSensor:
    """Ambient, low-frequency machine vitals -> a single mood-tint event per poll.
    `reader` returns (cpu_percent, battery_percent_or_None, is_charging)."""

    def __init__(self, reader=None):
        self._reader = reader or _psutil_reader

    def poll(self, now: float, spec, state) -> list:
        cpu, battery, charging = self._reader()
        if battery is not None and battery < balance.LOW_BATTERY_PCT and not charging:
            return [Event(EventType.LOW_BATTERY)]
        if cpu is not None and cpu >= balance.HIGH_CPU_PCT:
            return [Event(EventType.CPU_SPIKE)]
        return [Event(EventType.AMBIENT_CLEAR)]
