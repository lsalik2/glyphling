import dataclasses
from glyphling.core.generator import generate
from glyphling.core.events import EventType
from glyphling.core import quirks, balance

def _spec(seed, qs):
    return dataclasses.replace(generate(seed), quirks=qs)

def test_idle_quirk_deterministic_and_windowed():
    spec = _spec(7, ("hums to itself", "collects pebbles"))
    bucket = balance.QUIRK_BUCKET_MIN_SECONDS           # bond 100
    now = 50 * bucket                                    # a bucket start
    a = quirks.idle_quirk(spec, 100.0, now)
    assert a is not None and a[1] == "playful"
    assert quirks.idle_quirk(spec, 100.0, now) == a      # deterministic
    assert quirks.idle_quirk(spec, 100.0, now + balance.QUIRK_FIRE_WINDOW_SECONDS + 1) is None

def test_idle_quirk_none_without_idle_quirks():
    spec = _spec(7, ("sleeps upside-down", "sneezes when startled"))
    assert quirks.idle_quirk(spec, 100.0, 6000.0) is None

def test_low_bond_has_quiet_and_active_buckets():
    spec = _spec(7, ("hums to itself", "collects pebbles"))
    bucket = balance.QUIRK_BUCKET_MAX_SECONDS           # bond 0
    out = [quirks.idle_quirk(spec, 0.0, i * bucket) for i in range(20)]
    assert any(o is None for o in out) and any(o is not None for o in out)

def test_event_quirk_matches_startled_and_dev_activity():
    sneezer = _spec(7, ("sneezes when startled", "hums to itself"))
    assert quirks.event_quirk(sneezer, EventType.STARTLED)[1] == "startled"
    assert quirks.event_quirk(sneezer, EventType.COMMITTED) is None
    banger = _spec(7, ("headbangs to fast typing", "hums to itself"))
    assert quirks.event_quirk(banger, EventType.TESTS_PASSED)[1] == "excited"
    assert quirks.event_quirk(banger, EventType.STARTLED) is None

def test_has_pose_quirk():
    assert quirks.has_pose_quirk(_spec(7, ("sleeps upside-down", "hums to itself")), "upside_down")
    assert not quirks.has_pose_quirk(_spec(7, ("hums to itself", "collects pebbles")), "upside_down")

def test_high_bond_fires_always_and_favors_the_favorite():
    spec = _spec(7, ("hums to itself", "collects pebbles"))
    favorite = spec.quirks[spec.seed % 2]                 # = pool[seed % len(pool)]
    fav_lines = set(quirks.QUIRKS[favorite]["lines"])
    bucket = balance.QUIRK_BUCKET_MIN_SECONDS             # bonded -> smallest bucket
    seen = [quirks.idle_quirk(spec, 100.0, i * bucket) for i in range(60)]  # all at bucket starts
    assert all(s is not None for s in seen)              # bonded fires every in-window bucket
    fav_count = sum(1 for s in seen if s[0] in fav_lines)
    assert fav_count > len(seen) // 2                     # the favorite dominates at high bond
