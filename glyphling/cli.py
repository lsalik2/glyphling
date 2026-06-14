# glyphling/cli.py
import argparse
import os
import time
from pathlib import Path

from glyphling.core.generator import generate
from glyphling.core.renderer import render
from glyphling.core.events import EventType

def default_state_path() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "glyphling" / "pet.json"

def _cmd_hatch(seed: int) -> None:
    spec = generate(seed)
    s = spec.species
    print(f"{spec.name} — {s.archetype.value}, {s.circadian.value}, likes: {s.diet}")
    print(render(spec, "content", 0))
    print(f"quirks: {', '.join(spec.quirks)}")

def _cmd_rename(name: str) -> None:
    from glyphling.session import PetSession
    session = PetSession.start(default_state_path(), clock=time.time)
    session.action(EventType.RENAME, {"name": name})
    print(f"Renamed to {name}")

def _cmd_daemon(action: str) -> None:
    from glyphling import daemon
    path = default_state_path()
    if action == "start":
        daemon.start(path)
    elif action == "stop":
        daemon.stop(path)
    else:
        daemon.print_status(path)

def _cmd_run() -> None:
    from glyphling.session import PetSession
    from glyphling.tui.app import GlyphlingApp
    session = PetSession.start(default_state_path(), clock=time.time)
    GlyphlingApp(session).run()

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="glyphling", description="A procedural ASCII pet.")
    sub = parser.add_subparsers(dest="cmd")
    p_hatch = sub.add_parser("hatch", help="preview the creature for a seed")
    p_hatch.add_argument("seed", type=int)
    p_rename = sub.add_parser("rename", help="rename your pet")
    p_rename.add_argument("name")
    p_daemon = sub.add_parser("daemon", help="background companion: start|stop|status")
    p_daemon.add_argument("action", choices=["start", "stop", "status"])
    args = parser.parse_args(argv)

    if args.cmd == "hatch":
        _cmd_hatch(args.seed)
    elif args.cmd == "rename":
        _cmd_rename(args.name)
    elif args.cmd == "daemon":
        _cmd_daemon(args.action)
    else:
        _cmd_run()

if __name__ == "__main__":
    main()
