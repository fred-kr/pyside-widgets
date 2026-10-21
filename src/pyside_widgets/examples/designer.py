"""Launch Qt Designer with the pyside-widgets plugins registered."""

import os
import subprocess
from pathlib import Path


def run() -> None:
    plugin_path = Path(__file__).parent.parent / "plugins"
    os.environ["PYSIDE_DESIGNER_PLUGINS"] = str(plugin_path)
    subprocess.run(["pyside6-designer"], check=False)


if __name__ == "__main__":
    run()
