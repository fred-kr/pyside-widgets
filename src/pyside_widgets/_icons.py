import functools
from importlib.resources import files

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QIconEngine, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QStyleOption


def is_dark_palette(palette: QPalette | None = None) -> bool:
    """Whether ``palette`` (default: the application palette) has a dark window background."""
    palette = palette or QGuiApplication.palette()
    return palette.color(QPalette.ColorRole.Window).lightness() < 128


_clones: list[QIconEngine] = []


class _SchemeAwareIconEngine(QIconEngine):
    """
    Draws a bundled monochrome SVG as shipped on light palettes and recoloured white on dark palettes.

    The palette is read on every paint, so the icon follows a light/dark switch without being set again. The package
    cannot use ``QIcon.fromTheme`` for this because the icon theme name is global and belongs to the application.
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name
        self._source = QIcon(str(files("pyside_widgets") / "icons" / f"{name}.svg"))

    def clone(self) -> QIconEngine:
        # Qt takes ownership of the clone, but PySide deletes it with its last Python reference. Keeping that
        # reference costs one small object per clone; Qt only clones when a shared copy of the icon is modified.
        engine = _SchemeAwareIconEngine(self._name)
        _clones.append(engine)
        return engine

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        scale = painter.device().devicePixelRatioF()
        painter.drawPixmap(rect, self.scaledPixmap(rect.size(), mode, state, scale))

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        return self.scaledPixmap(size, mode, state, 1.0)

    def scaledPixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State, scale: float) -> QPixmap:
        if not is_dark_palette():
            return self._source.pixmap(size, scale, mode, state)

        pixmap = self._source.pixmap(size, scale, QIcon.Mode.Normal, state)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)  # keep alpha, replace color
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.white)
        painter.end()
        if mode != QIcon.Mode.Normal:
            # Same disabled/selected rendering Qt's own icon engines apply.
            pixmap = QApplication.style().generatedIconPixmap(mode, pixmap, QStyleOption())
        return pixmap


@functools.cache
def get_icon(name: str) -> QIcon:
    """
    Return the bundled icon ``icons/<name>.svg``, e.g. ``get_icon("ArrowReset")``.

    The icon is black on light palettes and white on dark palettes, and switches when the application palette changes.
    """
    return QIcon(_SchemeAwareIconEngine(name))
