from asciipet.core import balance

def test_decay_rates_present_and_positive():
    for key in ("fullness", "energy", "happiness", "cleanliness", "social"):
        assert balance.BASE_DECAY_PER_HOUR[key] > 0

def test_stage_thresholds_ascending():
    hours = [h for _, h in balance.STAGE_THRESHOLDS_HOURS]
    assert hours == sorted(hours)

def test_health_floor_below_max():
    assert 0 < balance.HEALTH_FLOOR < balance.HEALTH_MAX
