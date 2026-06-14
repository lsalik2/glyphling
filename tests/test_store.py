from glyphling import store
from glyphling.core.generator import generate
from glyphling.core.simulation import new_state

def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "pet.json"
    spec = generate(42)
    state = new_state()
    store.save(path, spec, state, now=1000.0)
    spec2, state2, last_tick = store.load(path)
    assert spec2 == spec
    assert state2.needs == state.needs
    assert last_tick == 1000.0

def test_save_creates_backup(tmp_path):
    path = tmp_path / "pet.json"
    spec, state = generate(1), new_state()
    store.save(path, spec, state, now=1.0)
    store.save(path, spec, state, now=2.0)
    assert (tmp_path / "pet.json.bak").exists()

def test_load_or_hatch_creates_then_loads(tmp_path):
    path = tmp_path / "pet.json"
    spec, state = store.load_or_hatch(path, now=1000.0, seed=7)
    assert path.exists()
    assert spec == generate(7)
    spec2, state2 = store.load_or_hatch(path, now=1000.0)
    assert spec2 == spec

def test_load_or_hatch_applies_catchup_decay(tmp_path):
    path = tmp_path / "pet.json"
    store.load_or_hatch(path, now=1000.0, seed=7)
    _, state = store.load_or_hatch(path, now=1000.0 + 3600 * 10)   # 10 hours later
    assert state.needs["fullness"] < 80.0
