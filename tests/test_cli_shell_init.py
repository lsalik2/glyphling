# tests/test_cli_shell_init.py
import glyphling.cli as cli

def test_shell_init_zsh(capsys):
    cli.main(["shell-init", "zsh"])
    out = capsys.readouterr().out
    assert "preexec" in out and "precmd" in out
    assert "shell-events.log" in out
    assert "glyphling shell hook" in out          # delimiters for easy removal

def test_shell_init_bash(capsys):
    cli.main(["shell-init", "bash"])
    out = capsys.readouterr().out
    assert "PROMPT_COMMAND" in out
    assert "shell-events.log" in out

def test_shell_init_autodetects_from_shell_env(monkeypatch, capsys):
    monkeypatch.setenv("SHELL", "/usr/bin/zsh")
    cli.main(["shell-init"])
    assert "preexec" in capsys.readouterr().out

def test_hooks_create_log_user_only():
    # Both hooks must write the (privacy-sensitive) log via a umask-077 subshell so it
    # stays 0600 even after the daemon drains and the shell recreates it.
    for shell in ("bash", "zsh"):
        assert "umask 077" in cli._HOOKS[shell]
