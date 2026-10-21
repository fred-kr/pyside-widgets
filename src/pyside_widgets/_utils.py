import enum

from PySide6.QtGui import QColor


class _Nothing(enum.Enum):
    NOTHING = enum.auto()

    def __repr__(self) -> str:
        return "NOTHING"

    def __bool__(self) -> bool:
        return False


NOTHING = _Nothing.NOTHING
"""Sentinel for "no value given", distinct from ``None``."""


def get_text_color(background_color: QColor) -> QColor:
    """Return black or white, whichever contrasts better with ``background_color``."""
    luminance = (
        (background_color.red() * 299) + (background_color.green() * 587) + (background_color.blue() * 114)
    ) // 1000
    return QColor(255, 255, 255) if luminance < 128 else QColor(0, 0, 0)
