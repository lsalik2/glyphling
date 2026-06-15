# glyphling/sensors/shell.py
"""Watches an opt-in shell-event log (commands + exit codes you ran), classifies each
into a dev reaction event, and drains the log so it never accumulates. Privacy: opt-in,
command lines only, local, drained continuously, removable."""
import shlex
from pathlib import Path

from glyphling import coord
from glyphling.core.events import Event, EventType

_TEST_PROGS = {"pytest", "jest", "vitest", "tox", "rspec", "phpunit"}
_TEST_SUB = {"npm": "test", "yarn": "test", "pnpm": "test",
             "cargo": "test", "go": "test", "mvn": "test", "gradle": "test"}
_BUILD_PROGS = {"make"}
_BUILD_SUB = {"npm": {"install", "ci"}, "yarn": {"install"}, "pnpm": {"install"},
              "cargo": {"build"}, "go": {"build"}, "docker": {"build"},
              "pip": {"install"}, "pip3": {"install"},
              "mvn": {"package", "install"}, "gradle": {"build"}}

def _tokens(command: str):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()

def _is_scary(prog, rest) -> bool:
    if prog == "rm" and any(t.startswith("-") and "r" in t.lower() for t in rest):
        return True
    if prog == "git" and "reset" in rest and "--hard" in rest:
        return True
    if prog == "git" and "push" in rest and any(f in rest for f in ("--force", "-f")):
        return True
    if prog == "dd" or prog.startswith("mkfs"):
        return True
    return False

def _is_test(prog, rest) -> bool:
    if prog in _TEST_PROGS:
        return True
    if prog in ("python", "python3"):
        return "pytest" in rest
    sub = _TEST_SUB.get(prog)
    return sub is not None and sub in rest

def _is_build(prog, rest) -> bool:
    if prog in _BUILD_PROGS:
        return True
    subs = _BUILD_SUB.get(prog)
    return subs is not None and any(s in rest for s in subs)

def classify(command: str, exit_code: int):
    """Map a shell command + exit code to a dev EventType, or None (no reaction)."""
    toks = _tokens(command)
    if not toks:
        return None
    prog, rest = toks[0], toks[1:]
    if _is_scary(prog, rest):
        return EventType.STARTLED
    if _is_test(prog, rest):
        return EventType.TESTS_PASSED if exit_code == 0 else EventType.TESTS_FAILED
    if _is_build(prog, rest):
        return EventType.BUILD_DONE if exit_code == 0 else EventType.BUILD_FAILED
    if prog == "git" and rest[:1] in (["commit"], ["push"]) and exit_code == 0:
        return EventType.COMMITTED
    return None

class ShellSensor:
    """Drains `shell-events.log` (beside the state file) each poll. Primes on first poll
    (discards any backlog) so a daemon (re)start never replays your history."""

    def __init__(self, state_path):
        self._log = Path(state_path).with_name("shell-events.log")
        self._primed = False

    def poll(self, now, spec, state) -> list:
        lines = coord.drain_lines(self._log)
        if not self._primed:
            self._primed = True
            return []
        events = []
        for line in lines:
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            try:
                exit_code = int(parts[0])
            except ValueError:
                continue
            et = classify(parts[1], exit_code)
            if et is not None:
                events.append(Event(et))
        return events
