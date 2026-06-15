import os
import stat
import sys

import pytest

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

def test_load_recovers_from_backup_when_state_corrupt(tmp_path):
    path = tmp_path / "pet.json"
    spec, state = generate(1), new_state()
    store.save(path, spec, state, now=1000.0)
    store.save(path, spec, state, now=2000.0)        # .bak now holds the 1000 version
    path.write_text("{ this is not valid json ")     # live file corrupted (partial write)
    _, _, last_tick = store.load(path)
    assert last_tick == 1000.0                        # recovered from .bak

def test_load_raises_when_neither_state_nor_backup_is_valid(tmp_path):
    path = tmp_path / "pet.json"
    path.write_text("garbage")                        # corrupt, no .bak at all
    with pytest.raises(ValueError):
        store.load(path)

def test_failed_save_preserves_previous_state(tmp_path, monkeypatch):
    path = tmp_path / "pet.json"
    store.save(path, generate(1), new_state(), now=1000.0)   # good v1 on disk
    import glyphling.store as store_mod
    def boom(src, dst):
        raise OSError("publish failed mid-save")
    monkeypatch.setattr(store_mod.os, "replace", boom)
    with pytest.raises(OSError):
        store.save(path, generate(1), new_state(), now=2000.0)
    monkeypatch.undo()
    _, _, last_tick = store.load(path)
    assert last_tick == 1000.0                        # a failed save never corrupts the live file

def test_save_leaves_no_temp_file(tmp_path):
    path = tmp_path / "pet.json"
    store.save(path, generate(1), new_state(), now=1.0)
    assert not (tmp_path / "pet.json.tmp").exists()
    store.load(path)                                  # and the published file is valid

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file permissions only")
def test_save_restricts_state_file_and_dir_permissions(tmp_path):
    d = tmp_path / "glyphling"
    path = d / "pet.json"
    store.save(path, generate(1), new_state(), now=1.0)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600   # pet.json may hold a private name
    assert stat.S_IMODE(os.stat(d).st_mode) == 0o700      # state dir is user-only

def test_pre_4a_state_without_playful_ttl_loads(tmp_path):
    import json, dataclasses
    from glyphling import store
    from glyphling.core.generator import generate
    from glyphling.core.simulation import new_state
    path = tmp_path / "pet.json"
    d = {"spec": store.spec_to_dict(generate(7)),
         "state": dataclasses.asdict(new_state()), "last_tick": 1000.0}
    d["state"].pop("playful_ttl")              # simulate a pre-4a save
    path.write_text(json.dumps(d))
    _, state, _ = store.load(path)
    assert state.playful_ttl == 0.0            # defaulted, loads fine
