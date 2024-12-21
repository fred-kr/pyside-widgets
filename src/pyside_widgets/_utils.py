import enum
import typing as t

import darkdetect
from PySide6 import QtCore, QtGui, QtWidgets


class Theme(enum.Enum):
    LIGHT = "Light"
    DARK = "Dark"
    AUTO = "Auto"


def is_dark_theme() -> bool:
    t = darkdetect.theme()
    t = Theme(t) if t else Theme.LIGHT
    return t == Theme.DARK


class _Nothing(enum.Enum):
    NOTHING = enum.auto()

    def __repr__(self) -> str:
        return "NOTHING"

    def __bool__(self) -> bool:
        return False


NOTHING = _Nothing.NOTHING


def set_font(
    widget: QtWidgets.QWidget | QtGui.QStandardItem, font_size: int = 14, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Normal
) -> None:
    font = widget.font()
    font.setPointSize(font_size)
    font.setWeight(weight)
    widget.setFont(font)
