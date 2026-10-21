"""PyInstaller hook directory, advertised through the ``pyinstaller40`` entry point in pyproject.toml."""

from pathlib import Path


def get_hook_dirs() -> list[str]:
    return [str(Path(__file__).parent)]
