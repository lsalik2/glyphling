"""All tunable simulation constants live here so feel can be tuned in one place."""

NEED_MIN = 0.0
NEED_MAX = 100.0
HEALTH_FLOOR = 5.0          # the pet can never drop below this -> it cannot die
HEALTH_MAX = 100.0
BOND_MAX = 100.0

# Need decay in points per hour while awake.
BASE_DECAY_PER_HOUR = {
    "fullness": 12.0,
    "energy": 8.0,
    "happiness": 6.0,
    "cleanliness": 4.0,
    "social": 7.0,
}

# Sleep dynamics.
SLEEP_ENERGY_REGEN_PER_HOUR = 20.0
SLEEP_DECAY_FACTOR = 0.4     # non-energy needs decay at this fraction while asleep

# Health buffer.
CRITICAL_NEED_THRESHOLD = 15.0
LOW_NEED_THRESHOLD = 30.0
SICK_HEALTH_THRESHOLD = 25.0
HEALTH_DECAY_PER_HOUR = 6.0  # per critical need
HEALTH_REGEN_PER_HOUR = 10.0 # when no needs are critical

# Bond.
BOND_PER_POSITIVE = 1.5

# Initial need value for a freshly hatched pet.
START_NEED = 80.0

# Life stages by effective hours = age_seconds * aging_rate / 3600.
# Below the first threshold the stage is "egg".
STAGE_THRESHOLDS_HOURS = [
    ("baby", 0.1),
    ("juvenile", 24.0),
    ("adult", 96.0),
    ("elder", 480.0),
]

# Catch-up clamp: never apply more than this much elapsed time at once (kindness cap).
CATCHUP_MAX_SECONDS = 14 * 24 * 3600

# --- Phase 2: daemon & sensors ---
DAEMON_INTERVAL_SECONDS = 10.0    # daemon tick cadence
DAEMON_STALE_SECONDS = 30.0       # a lock older than this => daemon considered dead

# Circadian sleep windows, in local clock hours [start, end).
DAY_START = 7                     # diurnal pets are awake from DAY_START
DAY_END = 21                      # ...until DAY_END
CREP_NAP_START = 11               # crepuscular pets nap midday
CREP_NAP_END = 15

# Vitals thresholds.
HIGH_CPU_PCT = 80.0               # sustained CPU at/above this -> "excited"
LOW_BATTERY_PCT = 20.0            # battery below this (and unplugged) -> "tired"

# --- Phase 3: dev reactions & presence ---
REACTION_TTL = 6.0                 # seconds a reaction speech bubble stays up
AWAY_THRESHOLD_SECONDS = 30 * 60   # idle gap that counts as "away" -> welcome-back on return
DEV_BOND = 0.5                     # tiny bond bump on a dev "win"

# --- Phase 4a: depth & payoff ---

# Stage decay multiplier (applied on top of metabolism). Babies burn hot; elders mellow; egg
# keeps the baseline (1.0) so a freshly-hatched pet decays normally from its first tick.
STAGE_DECAY_FACTOR = {"egg": 1.0, "baby": 1.3, "juvenile": 1.1, "adult": 1.0, "elder": 0.8}

# Per-need personality decay tilt: need -> (axis, weight). factor = clamp(1 + weight*axis, *CLAMP).
PERSONALITY_DECAY = {
    "social":      ("affection", 0.25),   # clingy (high affection) drains social faster
    "energy":      ("energy",    0.25),   # hyper burns energy faster
    "cleanliness": ("tidy",     -0.25),   # tidy stays clean longer
    "happiness":   ("playful",   0.25),   # playful needs play more often
}
PERSONALITY_DECAY_CLAMP = (0.5, 1.5)

# Mood inertia: a PLAY/PRAISE keeps the playful/excited mood this long, then it settles.
PLAY_MOOD_SECONDS = 180.0

# Bond tiers: (lower-bound-inclusive, name), ascending.
BOND_TIERS = [(0, "stranger"), (20, "acquaintance"), (40, "friend"), (60, "companion"), (80, "bonded")]
# Points shaved off LOW_NEED_THRESHOLD by tier (effective floor never below CRITICAL+2).
BOND_MOOD_FLOOR = {"stranger": 0, "acquaintance": 3, "friend": 6, "companion": 10, "bonded": 14}

# Idle quirk cadence.
QUIRK_BUCKET_MAX_SECONDS = 600.0   # ~10 min between idle quirks at bond 0
QUIRK_BUCKET_MIN_SECONDS = 120.0   # ~2 min at bond 100
QUIRK_FIRE_WINDOW_SECONDS = 10.0   # = daemon interval; one tick lands in the bucket's opening window
QUIRK_SILENCE_SLOTS = 3            # base "quiet bucket" slots; fewer as bond rises


def bond_tier(bond: float) -> str:
    name = BOND_TIERS[0][1]
    for lower, tier_name in BOND_TIERS:
        if bond >= lower:
            name = tier_name
    return name


def tier_index(bond: float) -> int:
    idx = 0
    for i, (lower, _name) in enumerate(BOND_TIERS):
        if bond >= lower:
            idx = i
    return idx
