# glyphling/sensors/clock.py
import time
from glyphling.core.events import Event, EventType
from glyphling.core import balance

def should_sleep(circadian: str, hour: int) -> bool:
    day = balance.DAY_START <= hour < balance.DAY_END
    if circadian == "nocturnal":
        return day
    if circadian == "crepuscular":
        return balance.CREP_NAP_START <= hour < balance.CREP_NAP_END
    return not day  # diurnal (and default)

class ClockSensor:
    """Edge-triggered circadian sleep/wake based on the creature's circadian type."""

    def __init__(self, hour_fn=None):
        self._hour_fn = hour_fn or (lambda now: time.localtime(now).tm_hour)

    def poll(self, now: float, spec, state) -> list:
        hour = self._hour_fn(now)
        night = should_sleep(spec.species.circadian.value, hour)
        if night and not state.asleep:
            return [Event(EventType.NIGHTFALL)]
        if (not night) and state.asleep and state.sleep_reason == "circadian":
            return [Event(EventType.MORNING)]
        return []
