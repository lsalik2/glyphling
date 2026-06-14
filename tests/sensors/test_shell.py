# tests/sensors/test_shell.py
from glyphling.sensors.shell import classify, ShellSensor
from glyphling.core.events import EventType

def test_classify_tests():
    assert classify("pytest -q", 0) == EventType.TESTS_PASSED
    assert classify("pytest -q", 1) == EventType.TESTS_FAILED
    assert classify("npm test", 0) == EventType.TESTS_PASSED
    assert classify("cargo test", 1) == EventType.TESTS_FAILED

def test_classify_builds():
    assert classify("make", 0) == EventType.BUILD_DONE
    assert classify("npm install", 0) == EventType.BUILD_DONE
    assert classify("cargo build", 1) == EventType.BUILD_FAILED

def test_classify_git_win_only_on_success():
    assert classify("git commit -m 'make it work'", 0) == EventType.COMMITTED
    assert classify("git push", 0) == EventType.COMMITTED
    assert classify("git commit -m x", 1) is None

def test_classify_scary_regardless_of_exit():
    assert classify("rm -rf build", 0) == EventType.STARTLED
    assert classify("git reset --hard HEAD~1", 0) == EventType.STARTLED
    assert classify("git push --force", 0) == EventType.STARTLED

def test_classify_ignores_ordinary_commands():
    assert classify("ls -la", 0) is None
    assert classify("cd ~/projects", 0) is None
    assert classify("grep -r foo .", 1) is None

def test_commit_message_does_not_trip_build_or_test():
    assert classify("git commit -m 'make the tests pass'", 0) == EventType.COMMITTED

def test_shell_sensor_primes_then_classifies(tmp_path):
    log = tmp_path / "shell-events.log"
    log.write_text("0\tgit commit -m old\n")
    sensor = ShellSensor(tmp_path / "pet.json")
    assert sensor.poll(0.0, None, None) == []             # first poll primes & discards backlog
    assert not log.exists()                                # log was drained
    log.write_text("0\tgit commit -m new\n1\tls\n")
    events = sensor.poll(0.0, None, None)
    assert [e.type for e in events] == [EventType.COMMITTED]   # ls ignored
    assert sensor.poll(0.0, None, None) == []
