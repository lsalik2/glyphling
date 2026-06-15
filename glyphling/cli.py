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
    art = render(spec, "content", 0).strip("\n")          # drop the reserved bubble line
    print(art)
    print()
    print(f"{spec.name}  (seed {spec.seed})")
    print(f"  {s.archetype.value} · {s.circadian.value} · likes {s.diet} · says \"{s.vocab}\"")
    print(f"  quirks: {', '.join(spec.quirks)}")

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

_ZSH_HOOK = r'''# >>> glyphling shell hook >>>  (remove this block to uninstall)
# Privacy: logs only the command line + exit code you run (already in your shell history),
# never keystrokes typed into programs. The log is local (created user-only, 0600) and
# drained by the daemon.
_glyphling_log="${XDG_DATA_HOME:-$HOME/.local/share}/glyphling/shell-events.log"
mkdir -p "${_glyphling_log:h}" 2>/dev/null
_glyphling_preexec() { _GLYPHLING_CMD="$1" }
_glyphling_precmd() {
  local ex=$?
  [ -n "$_GLYPHLING_CMD" ] && ( umask 077; printf '%s\t%s\n' "$ex" "$_GLYPHLING_CMD" >> "$_glyphling_log" ) 2>/dev/null
  _GLYPHLING_CMD=""
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec _glyphling_preexec
add-zsh-hook precmd _glyphling_precmd
# <<< glyphling shell hook <<<'''

_BASH_HOOK = r'''# >>> glyphling shell hook >>>  (remove this block to uninstall)
# Privacy: logs only the command line + exit code you run (already in your shell history),
# never keystrokes typed into programs. The log is local (created user-only, 0600) and
# drained by the daemon.
_glyphling_log="${XDG_DATA_HOME:-$HOME/.local/share}/glyphling/shell-events.log"
mkdir -p "$(dirname "$_glyphling_log")" 2>/dev/null
_glyphling_record() {
  local ex=$?
  local cmd
  cmd=$(history 1 2>/dev/null | sed 's/^ *[0-9]* *//')
  if [ -n "$cmd" ] && [ "$cmd" != "$_GLYPHLING_LAST" ]; then
    ( umask 077; printf '%s\t%s\n' "$ex" "$cmd" >> "$_glyphling_log" ) 2>/dev/null
    _GLYPHLING_LAST="$cmd"
  fi
}
case "$PROMPT_COMMAND" in
  *_glyphling_record*) ;;
  *) PROMPT_COMMAND="_glyphling_record${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
esac
# <<< glyphling shell hook <<<'''

_HOOKS = {"bash": _BASH_HOOK, "zsh": _ZSH_HOOK}

def _detect_shell() -> str:
    shell = os.path.basename(os.environ.get("SHELL", ""))
    return shell if shell in _HOOKS else "bash"

def _cmd_shell_init(shell) -> None:
    shell = shell or _detect_shell()
    hook = _HOOKS.get(shell)
    if hook is None:
        print(f"unsupported shell: {shell} (supported: bash, zsh)")
        return
    print(f"# Paste this into your ~/.{shell}rc, then restart your shell.")
    print(hook)

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="glyphling", description="A procedural ASCII pet.")
    sub = parser.add_subparsers(dest="cmd")
    p_hatch = sub.add_parser("hatch", help="preview the creature for a seed")
    p_hatch.add_argument("seed", type=int)
    p_rename = sub.add_parser("rename", help="rename your pet")
    p_rename.add_argument("name")
    p_daemon = sub.add_parser("daemon", help="background companion: start|stop|status")
    p_daemon.add_argument("action", choices=["start", "stop", "status"])
    p_shell = sub.add_parser("shell-init", help="print a shell hook so the pet notices your commands")
    p_shell.add_argument("shell", nargs="?", choices=["bash", "zsh"], default=None)
    args = parser.parse_args(argv)

    if args.cmd == "hatch":
        _cmd_hatch(args.seed)
    elif args.cmd == "rename":
        _cmd_rename(args.name)
    elif args.cmd == "daemon":
        _cmd_daemon(args.action)
    elif args.cmd == "shell-init":
        _cmd_shell_init(args.shell)
    else:
        _cmd_run()

if __name__ == "__main__":
    main()
