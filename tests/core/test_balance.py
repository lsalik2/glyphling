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

def test_bond_tier_boundaries():
    from glyphling.core.balance import bond_tier, tier_index
    assert bond_tier(0) == "stranger"
    assert bond_tier(19.9) == "stranger"
    assert bond_tier(20) == "acquaintance"
    assert bond_tier(40) == "friend"
    assert bond_tier(60) == "companion"
    assert bond_tier(80) == "bonded"
    assert bond_tier(100) == "bonded"
    assert tier_index(0) == 0
    assert tier_index(20) == 1
    assert tier_index(59.9) == 2
    assert tier_index(80) == 4

def test_phase4a_constants_present():
    from glyphling.core import balance
    assert balance.STAGE_DECAY_FACTOR["egg"] == 1.0      # baseline: fresh pets decay normally
    assert balance.STAGE_DECAY_FACTOR["baby"] > balance.STAGE_DECAY_FACTOR["adult"]
    assert balance.STAGE_DECAY_FACTOR["elder"] < balance.STAGE_DECAY_FACTOR["adult"]
    assert balance.PLAY_MOOD_SECONDS == 180.0
    assert balance.BOND_MOOD_FLOOR["bonded"] == 14
