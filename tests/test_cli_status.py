def test_cli_status_is_read_only(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    import glyphling.cli as cli
    from glyphling import store
    from glyphling.core.generator import generate
    from glyphling.core.simulation import new_state
    path = tmp_path / "glyphling" / "pet.json"
    store.save(path, generate(7), new_state(), now=1000.0)
    before = path.read_bytes()
    cli.main(["status"])
    out = capsys.readouterr().out
    assert generate(7).name in out
    assert path.read_bytes() == before          # pure reader: state unchanged

def test_cli_status_unhatched(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    import glyphling.cli as cli
    cli.main(["status"])
    assert "no glyphling yet" in capsys.readouterr().out
