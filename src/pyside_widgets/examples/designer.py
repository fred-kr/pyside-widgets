"""Launch Qt Designer with the pyside-widgets plugins registered. Run with ``uv run pyside-widgets-designer``."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _append_path(env: dict[str, str], variable: str, path: Path) -> None:
    existing = env.get(variable)
    env[variable] = os.pathsep.join([existing, str(path)]) if existing else str(path)


def designer_environment() -> dict[str, str]:
    """
    The current environment, extended so that Designer finds the plugins and can import ``pyside_widgets``.

    Existing values of ``PYSIDE_DESIGNER_PLUGINS`` and ``PYTHONPATH`` are kept; the new entries are appended.
    """
    env = dict(os.environ)
    package_dir = Path(__file__).parent.parent
    _append_path(env, "PYSIDE_DESIGNER_PLUGINS", package_dir / "plugins")
    # Designer's embedded interpreter puts site-packages on sys.path but does not process .pth files, so a package
    # installed in editable mode (uv sync, pip install -e) is invisible to it without this.
    _append_path(env, "PYTHONPATH", package_dir.parent)
    return env


def designer_executable() -> str:
    """
    The ``pyside6-designer`` installed next to the running interpreter, or the bare name as a PATH fallback.

    Designer must run in the environment that has ``pyside_widgets`` installed, otherwise the plugins fail to import.
    """
    return shutil.which("pyside6-designer", path=str(Path(sys.executable).parent)) or "pyside6-designer"


def run() -> None:
    subprocess.run([designer_executable()], env=designer_environment(), check=False)


if __name__ == "__main__":
    run()
