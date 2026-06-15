def test_format_line_gauges_and_compact():
    from glyphling.statusline import format_line
    from glyphling.core.generator import generate
    from glyphling.core.simulation import new_state
    spec = generate(7); st = new_state()
    line = format_line(spec, st)
    assert spec.name in line and "food" in line and "bond: stranger" in line
    compact = format_line(spec, st, compact=True)
    assert spec.name in compact and "·" in compact and "food" not in compact
