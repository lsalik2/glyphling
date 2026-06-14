# glyphling/core/simulation.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

from glyphling.core import balance
from glyphling.core.events import (
    Event, EventType, EVENT_EFFECTS, POSITIVE_BOND_EVENTS, WAKING_EVENTS, AMBIENT_MOOD_EVENTS,
)
from glyphling.core.spec import CreatureSpec

NEED_KEYS = ("fullness", "energy", "happiness", "cleanliness", "social")

class Mood(str, Enum):
    CONTENT = "content"
    HAPPY = "happy"
    EXCITED = "excited"
    PLAYFUL = "playful"
    HUNGRY = "hungry"
    TIRED = "tired"
    LONELY = "lonely"
    GRUMPY = "grumpy"
    SAD = "sad"
    SICK = "sick"
    SLEEPING = "sleeping"

@dataclass
class PetState:
    needs: dict
    health: float
    mood: str
    bond: float
    age_seconds: float
    stage: str
    asleep: bool
    recent_events: list = field(default_factory=list)
    sleep_reason: str = "none"     # "none" | "manual" | "circadian"
    ambient_mood: str = "none"     # "none" | "excited" | "tired"  (set by vitals sensor)

def new_state() -> PetState:
    return PetState(
        needs={k: balance.START_NEED for k in NEED_KEYS},
        health=balance.HEALTH_MAX,
        mood=Mood.CONTENT.value,
        bond=0.0,
        age_seconds=0.0,
        stage="egg",
        asleep=False,
        recent_events=[],
    )

def stage_for_age(effective_hours: float) -> str:
    stage = "egg"
    for name, threshold in balance.STAGE_THRESHOLDS_HOURS:
        if effective_hours >= threshold:
            stage = name
    return stage

def _clamp_need(value: float) -> float:
    return max(balance.NEED_MIN, min(balance.NEED_MAX, value))

def derive_mood(state: PetState, personality: dict) -> str:
    if state.asleep:
        return Mood.SLEEPING.value
    if state.health < balance.SICK_HEALTH_THRESHOLD:
        return Mood.SICK.value
    worst = min(NEED_KEYS, key=lambda k: state.needs[k])
    if state.needs[worst] < balance.LOW_NEED_THRESHOLD:
        return {
            "fullness": Mood.HUNGRY,
            "energy": Mood.TIRED,
            "social": Mood.LONELY,
            "cleanliness": Mood.GRUMPY,
            "happiness": Mood.SAD,
        }[worst].value
    last = state.recent_events[-1] if state.recent_events else None
    if last in (EventType.PLAY.value, EventType.PRAISE.value):
        if personality.get("energy", 0.0) > 0.3:
            return Mood.EXCITED.value
        return Mood.PLAYFUL.value
    if state.ambient_mood == "excited":
        return Mood.EXCITED.value
    if state.ambient_mood == "tired":
        return Mood.TIRED.value
    if all(state.needs[k] > 70.0 for k in NEED_KEYS):
        return Mood.HAPPY.value
    return Mood.CONTENT.value

def _apply_event(state: PetState, event: Event, spec: CreatureSpec) -> None:
    et = event.type
    if et == EventType.REST:
        if state.asleep:
            state.asleep, state.sleep_reason = False, "none"
        else:
            state.asleep, state.sleep_reason = True, "manual"
        return
    if et == EventType.NIGHTFALL:
        state.asleep, state.sleep_reason = True, "circadian"
        return
    if et == EventType.MORNING:
        if state.sleep_reason == "circadian":
            state.asleep, state.sleep_reason = False, "none"
        return
    if et in AMBIENT_MOOD_EVENTS:
        state.ambient_mood = AMBIENT_MOOD_EVENTS[et]
        return
    # Deliberate, need-affecting interactions.
    effects = EVENT_EFFECTS.get(et, {})
    for need, delta in effects.items():
        if delta > 0:
            applied = delta * (1.0 - state.needs[need] / balance.NEED_MAX)  # diminishing returns
        else:
            applied = delta
        state.needs[need] = _clamp_need(state.needs[need] + applied)
    if et in POSITIVE_BOND_EVENTS:
        state.bond = min(balance.BOND_MAX, state.bond + balance.BOND_PER_POSITIVE)
    if et in WAKING_EVENTS:
        state.asleep, state.sleep_reason = False, "none"
    state.recent_events.append(et.value)
    state.recent_events[:] = state.recent_events[-5:]

def advance(state: PetState, elapsed_seconds: float, events: list, spec: CreatureSpec) -> PetState:
    hours = max(0.0, elapsed_seconds) / 3600.0
    metabolism = spec.species.metabolism

    # 1. Time decay.
    for k in NEED_KEYS:
        if state.asleep and k == "energy":
            state.needs[k] = _clamp_need(state.needs[k] + balance.SLEEP_ENERGY_REGEN_PER_HOUR * hours)
            continue
        rate = balance.BASE_DECAY_PER_HOUR[k] * metabolism
        if state.asleep:
            rate *= balance.SLEEP_DECAY_FACTOR
        state.needs[k] = _clamp_need(state.needs[k] - rate * hours)

    # 2. Events (user actions + future sensor events).
    for event in events:
        _apply_event(state, event, spec)

    # 3. Health buffer (suffers but survives).
    critical = sum(1 for k in NEED_KEYS if state.needs[k] < balance.CRITICAL_NEED_THRESHOLD)
    if critical:
        state.health -= balance.HEALTH_DECAY_PER_HOUR * critical * hours
    else:
        state.health += balance.HEALTH_REGEN_PER_HOUR * hours
    state.health = max(balance.HEALTH_FLOOR, min(balance.HEALTH_MAX, state.health))

    # 4. Age and stage.
    state.age_seconds += max(0.0, elapsed_seconds)
    state.stage = stage_for_age(state.age_seconds * spec.species.aging_rate / 3600.0)

    # 5. Mood.
    state.mood = derive_mood(state, spec.personality)
    return state
