from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

type ColorLike = Qt.GlobalColor | QColor | str
"""Anything ``QColor(...)`` accepts as its only argument."""


def get_text_color(background_color: QColor) -> QColor:
    """Return black or white, whichever contrasts better with ``background_color``."""
    luminance = (
        (background_color.red() * 299) + (background_color.green() * 587) + (background_color.blue() * 114)
    ) // 1000
    return QColor(255, 255, 255) if luminance < 128 else QColor(0, 0, 0)


def scaled_font(font: QFont, factor: float) -> QFont:
    """Return a copy of ``font`` whose size is multiplied by ``factor``, in whichever unit ``font`` uses."""
    scaled = QFont(font)
    if font.pointSizeF() > 0:
        scaled.setPointSizeF(font.pointSizeF() * factor)
    else:
        scaled.setPixelSize(max(1, round(font.pixelSize() * factor)))
    return scaled
