import functools
from importlib.resources import files

from PySide6.QtGui import QIcon


@functools.cache
def get_icon(name: str) -> QIcon:
    """Load ``icons/<name>.svg`` from the package, e.g. ``get_icon("ArrowReset")``."""
    return QIcon(str(files("pyside_widgets") / "icons" / f"{name}.svg"))
