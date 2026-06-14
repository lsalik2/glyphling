# glyphling/sensors/base.py
from typing import Protocol

class Sensor(Protocol):
    def poll(self, now: float, spec, state) -> list:
        """Return a list of Event from observing the world at time `now`."""
        ...
