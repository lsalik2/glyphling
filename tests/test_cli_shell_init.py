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
