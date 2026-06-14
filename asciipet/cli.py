# asciipet/cli.py
import argparse
import os
import time
from pathlib import Path

from asciipet.core.generator import generate
from asciipet.core.renderer import render
from asciipet.core.events import EventType

def default_state_path() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "asciipet" / "pet.json"

def _cmd_hatch(seed: int) -> None:
    spec = generate(seed)
    s = spec.species
    print(f"{spec.name} — {s.archetype.value}, {s.circadian.value}, likes: {s.diet}")
    print(render(spec, "content", 0))
    print(f"quirks: {', '.join(spec.quirks)}")

def _cmd_rename(name: str) -> None:
    from asciipet.session import PetSession
    session = PetSession.start(default_state_path(), clock=time.time)
    session.action(EventType.RENAME, {"name": name})
    print(f"Renamed to {name}")

def _cmd_run() -> None:
    from asciipet.session import PetSession
    from asciipet.tui.app import AsciiPetApp
    session = PetSession.start(default_state_path(), clock=time.time)
    AsciiPetApp(session).run()

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="asciipet", description="A procedural ASCII pet.")
    sub = parser.add_subparsers(dest="cmd")
    p_hatch = sub.add_parser("hatch", help="preview the creature for a seed")
    p_hatch.add_argument("seed", type=int)
    p_rename = sub.add_parser("rename", help="rename your pet")
    p_rename.add_argument("name")
    args = parser.parse_args(argv)

    if args.cmd == "hatch":
        _cmd_hatch(args.seed)
    elif args.cmd == "rename":
        _cmd_rename(args.name)
    else:
        _cmd_run()
