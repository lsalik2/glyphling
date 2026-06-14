import importlib

def test_package_imports():
    assert importlib.import_module("asciipet") is not None
