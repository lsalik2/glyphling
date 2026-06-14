# asciipet/cli.py
import argparse
from asciipet.core.generator import generate
from asciipet.core.renderer import render

def _cmd_hatch(seed: int) -> None:
    spec = generate(seed)
    s = spec.species
    print(f"{spec.name} — {s.archetype.value}, {s.circadian.value}, likes: {s.diet}")
    print(render(spec, "content", 0))
    print(f"quirks: {', '.join(spec.quirks)}")

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="asciipet")
    sub = parser.add_subparsers(dest="cmd")
    p_hatch = sub.add_parser("hatch", help="preview the creature for a seed")
    p_hatch.add_argument("seed", type=int)
    args = parser.parse_args(argv)

    if args.cmd == "hatch":
        _cmd_hatch(args.seed)
    else:
        parser.print_help()
