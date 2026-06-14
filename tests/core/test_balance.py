from glyphling.core import balance

def test_decay_rates_present_and_positive():
    for key in ("fullness", "energy", "happiness", "cleanliness", "social"):
        assert balance.BASE_DECAY_PER_HOUR[key] > 0

def test_stage_thresholds_ascending():
    hours = [h for _, h in balance.STAGE_THRESHOLDS_HOURS]
    assert hours == sorted(hours)

def test_health_floor_below_max():
    assert 0 < balance.HEALTH_FLOOR < balance.HEALTH_MAX

def test_phase2_constants_present_and_sane():
    assert balance.DAEMON_INTERVAL_SECONDS > 0
    assert balance.DAEMON_STALE_SECONDS > balance.DAEMON_INTERVAL_SECONDS
    assert 0 <= balance.DAY_START < balance.DAY_END <= 24
    assert 0 <= balance.CREP_NAP_START < balance.CREP_NAP_END <= 24
    assert 0 < balance.HIGH_CPU_PCT <= 100
    assert 0 < balance.LOW_BATTERY_PCT <= 100

def test_phase3_constants_present_and_sane():
    assert balance.REACTION_TTL > 0
    assert balance.AWAY_THRESHOLD_SECONDS >= 60
    assert 0 < balance.DEV_BOND <= balance.BOND_PER_POSITIVE
