from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("glyphling")
except PackageNotFoundError:  # running from an uninstalled source tree
    __version__ = "0+unknown"
