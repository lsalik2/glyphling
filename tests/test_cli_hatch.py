# tests/test_cli_hatch.py
from glyphling.cli import main

def test_hatch_prints_creature(capsys):
    main(["hatch", "42"])
    out = capsys.readouterr().out
    assert "blob" in out or "critter" in out      # species line
    assert "\n" in out.strip()                     # multi-line art rendered

def test_hatch_output_is_clean_and_shows_seed(capsys):
    main(["hatch", "42"])
    out = capsys.readouterr().out
    assert not out.startswith("\n")                # no awkward leading blank line
    assert "seed 42" in out                        # reproducible: shows the seed used
    assert "quirks:" in out

def test_hatch_art_is_mono_when_not_a_tty(capsys):
    from glyphling.cli import main
    main(["hatch", "42"])
    out = capsys.readouterr().out
    assert "\x1b[" not in out          # no ANSI escapes when captured / piped
    assert "rgb(" not in out            # markup parsed away, not leaked literally
    assert "seed 42" in out             # the rest of the output is intact
