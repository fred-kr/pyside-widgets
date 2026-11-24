from PySide6.QtCore import Property, Qt, Signal, Slot
from PySide6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QPalette, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QStyleOptionFocusRect,
    QStylePainter,
    QWidget,
)

from pyside_widgets._utils import ColorLike, get_text_color

_SWATCH_BORDER = QColor(128, 128, 128)
"""Mid grey, visible around a swatch on light and on dark buttons."""


class ColorPickerButton(QPushButton):
    """
    A button that shows a color and opens a color dialog when clicked.

    The color is shown either as an icon next to the text or as the background of the whole button.
    """

    sig_color_changed = Signal(QColor)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        color: QColor | None = None,
        show_alpha: bool = False,
        show_icon: bool = True,
        show_text: bool = True,
    ) -> None:
        """
        Args:
            parent: Parent widget.
            color: Initial color. None or an invalid color selects the palette's accent color.
            show_alpha: Whether the dialog offers an alpha channel and the text includes it.
            show_icon: Show the color as an icon (True) or as the button background (False).
            show_text: Show the color name as the button text.
        """
        super().__init__(parent)

        if color is None or not color.isValid():
            color = self.palette().color(QPalette.ColorRole.Accent)
        self._color = QColor(color)
        self._show_alpha = show_alpha
        self._show_icon = show_icon
        self._show_text = show_text

        self._refresh()
        self.clicked.connect(self._on_clicked)

    def get_color(self) -> QColor:
        return self._color

    @Slot(QColor)
    def set_color(self, color: ColorLike) -> None:
        """Set the current color. Invalid colors are ignored. Emits ``sig_color_changed`` if the color changes."""
        color = QColor(color)
        if not color.isValid() or color == self._color:
            return
        self._color = color
        self._refresh()
        self.sig_color_changed.emit(self._color)

    def get_show_alpha_channel(self) -> bool:
        """Whether the color dialog offers an alpha channel and the text includes it."""
        return self._show_alpha

    @Slot(bool)
    def set_show_alpha_channel(self, value: bool) -> None:
        self._show_alpha = value
        self._refresh()

    def get_show_as_icon(self) -> bool:
        """Whether the color is shown as an icon (True) or as the button background (False)."""
        return self._show_icon

    @Slot(bool)
    def set_show_as_icon(self, value: bool) -> None:
        self._show_icon = value
        self._refresh()

    def get_show_text(self) -> bool:
        """Whether the color name is shown as the button text."""
        return self._show_text

    @Slot(bool)
    def set_show_text(self, value: bool) -> None:
        self._show_text = value
        self._refresh()

    def _refresh(self) -> None:
        name_format = QColor.NameFormat.HexArgb if self._show_alpha else QColor.NameFormat.HexRgb
        # The leading space separates the text from the swatch icon.
        self.setText(" " + self._color.name(name_format) if self._show_text else "")
        self.setIcon(self._swatch_icon() if self._show_icon else QIcon())
        self.update()

    def _swatch_icon(self) -> QIcon:
        size = self.iconSize()
        ratio = self.devicePixelRatioF()
        pixmap = QPixmap(size * ratio)
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(self._color)
        with QPainter(pixmap) as painter:
            painter.setPen(_SWATCH_BORDER)
            painter.drawRect(0, 0, size.width() - 1, size.height() - 1)
        return QIcon(pixmap)

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._show_icon:
            super().paintEvent(event)
            return

        # Background mode: the style draws the button frame, the color fills the area inside it. A style sheet would
        # be shorter, but it replaces the native button rendering and overrides the application's own style sheet.
        option = QStyleOptionButton()
        self.initStyleOption(option)
        style = self.style()
        painter = QStylePainter(self)  # not a "with" block: __enter__ is typed as returning a plain QPainter
        painter.drawControl(QStyle.ControlElement.CE_PushButtonBevel, option)
        if not self.isEnabled():
            painter.setOpacity(0.4)
        contents = style.subElementRect(QStyle.SubElement.SE_PushButtonContents, option, self)
        painter.fillRect(contents, self._color)
        painter.setPen(get_text_color(self._color))
        painter.drawText(contents, Qt.AlignmentFlag.AlignCenter, self.text().strip())
        painter.setOpacity(1.0)

        if self.hasFocus():
            focus = QStyleOptionFocusRect()
            focus.initFrom(self)
            focus.rect = style.subElementRect(QStyle.SubElement.SE_PushButtonFocusRect, option, self)
            painter.drawPrimitive(QStyle.PrimitiveElement.PE_FrameFocusRect, focus)
        painter.end()

    @Slot()
    def _on_clicked(self) -> None:
        options = QColorDialog.ColorDialogOption(0)
        if self._show_alpha:
            options |= QColorDialog.ColorDialogOption.ShowAlphaChannel
        self.set_color(QColorDialog.getColor(self._color, self, options=options))

    color = Property(QColor, get_color, set_color, notify=sig_color_changed, user=True)
    showAlphaChannel = Property(bool, get_show_alpha_channel, set_show_alpha_channel)
    showAsIcon = Property(bool, get_show_as_icon, set_show_as_icon)
    showText = Property(bool, get_show_text, set_show_text)

    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setColor = set_color
    setShowAlphaChannel = set_show_alpha_channel
    setShowAsIcon = set_show_as_icon
    setShowText = set_show_text
