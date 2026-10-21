from PySide6.QtCore import Property, Signal, Slot
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget

from pyside_widgets._utils import get_text_color


class ColorPickerButton(QPushButton):
    """
    A button that shows a color and opens a color dialog when clicked.
    """

    sig_color_changed = Signal(QColor)

    def __init__(
        self,
        parent: QWidget | None = None,
        color: QColor | None = None,
        show_alpha: bool = False,
        show_icon: bool = True,
        show_text: bool = True,
    ) -> None:
        super().__init__(parent)

        self._color = color or self.palette().color(QPalette.ColorRole.Accent)
        self._show_alpha = show_alpha
        self._show_icon = show_icon
        self._show_text = show_text

        self.set_color(self._color)
        self.clicked.connect(self._on_clicked)

    @property
    def text_fmt(self) -> QColor.NameFormat:
        """Color name format for the button text, with or without alpha."""
        return QColor.NameFormat.HexArgb if self._show_alpha else QColor.NameFormat.HexRgb

    def get_show_alpha_channel(self) -> bool:
        """Whether the color dialog offers an alpha channel and the text includes it."""
        return self._show_alpha

    def set_show_alpha_channel(self, value: bool) -> None:
        self._show_alpha = value
        self._refresh()

    def get_show_as_icon(self) -> bool:
        """Whether the color is shown as an icon (True) or as the button background (False)."""
        return self._show_icon

    def set_show_as_icon(self, value: bool) -> None:
        self._show_icon = value
        self._refresh()

    def get_show_text(self) -> bool:
        """Whether the color name is shown as the button text."""
        return self._show_text

    def set_show_text(self, value: bool) -> None:
        self._show_text = value
        self._refresh()

    def set_color(self, color: QColor) -> None:
        """Set the current color. Invalid colors are ignored. Emits ``sig_color_changed`` if the color changes."""
        if not color.isValid():
            return
        if color != self._color:
            self._color = color
            self.sig_color_changed.emit(self._color)
        self._refresh()

    def _refresh(self) -> None:
        self.setText(" " + self._color.name(self.text_fmt) if self._show_text else "")

        if self._show_icon:
            self.setStyleSheet("")
            pixmap = QPixmap(self.iconSize())
            pixmap.fill(self._color)
            painter = QPainter(pixmap)
            pen = QPen(QColor("black"))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(pixmap.rect().adjusted(0, 0, -1, -1))
            painter.end()
            self.setIcon(pixmap)
        else:
            self.setIcon(QIcon())
            text_color = get_text_color(self._color)
            self.setStyleSheet(
                f"ColorPickerButton {{ background-color: {self._color.name()}; color: {text_color.name()}; }}"
            )

    def color(self) -> QColor:
        return self._color

    @Slot()
    def _on_clicked(self) -> None:
        options = QColorDialog.ColorDialogOption(0)
        if self._show_alpha:
            options |= QColorDialog.ColorDialogOption.ShowAlphaChannel
        self.set_color(QColorDialog.getColor(self._color, self, options=options))

    showAlphaChannel = Property(bool, get_show_alpha_channel, set_show_alpha_channel)
    showAsIcon = Property(bool, get_show_as_icon, set_show_as_icon)
    showText = Property(bool, get_show_text, set_show_text)
