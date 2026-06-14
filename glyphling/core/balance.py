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
