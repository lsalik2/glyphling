import importlib
import importlib.metadata
import re

import glyphling


def test_version_matches_installed_metadata():
    assert glyphling.__version__ == importlib.metadata.version("glyphling")


def test_version_starts_with_release_segment():
    assert re.match(r"^\d+(\.\d+)*", glyphling.__version__)


def test_version_falls_back_when_not_installed(monkeypatch):
    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    try:
        importlib.reload(glyphling)
        assert glyphling.__version__ == "0+unknown"
    finally:
        monkeypatch.undo()
        importlib.reload(glyphling)
    assert glyphling.__version__ == importlib.metadata.version("glyphling")
