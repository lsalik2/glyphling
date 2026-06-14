# tests/test_cli_hatch.py
from glyphling.cli import main

def test_hatch_prints_creature(capsys):
    main(["hatch", "42"])
    out = capsys.readouterr().out
    assert "blob" in out or "critter" in out      # species line
    assert "\n" in out.strip()                     # multi-line art rendered
