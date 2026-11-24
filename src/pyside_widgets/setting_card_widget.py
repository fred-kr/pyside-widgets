from PySide6.QtCore import Property, QEvent, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QPalette
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pyside_widgets._icons import get_icon, is_dark_palette
from pyside_widgets._utils import scaled_font

_TITLE_FONT_SCALE = 1.15
_DESCRIPTION_FONT_SCALE = 0.9


class _IconLabel(QWidget):
    """Paints an icon on every repaint, so theme icons and scheme-aware icons follow a light/dark switch."""

    def __init__(self, icon: QIcon, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.icon = icon

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self) as painter:
            self.icon.paint(painter, self.rect())


class SettingCard(QFrame):
    """
    A card with an icon, title, description, an editor widget and a reset button.

    Modelled on ``qfluentwidgets.SettingCard`` without the qfluentwidgets dependency. Fonts are derived from the
    widget font and colors from the widget palette, so the card follows the application's font and its light or dark
    theme. The card sets no style sheet, so nothing leaks into the editor widget.

    The card does not know how to reset its editor. Connect ``sig_reset_clicked``:

        card = SettingCard(title="Sampling rate", editor_widget=spin_box)
        card.sig_reset_clicked.connect(lambda: spin_box.setValue(100))
    """

    sig_reset_clicked = Signal()
    """Emitted when the reset button is clicked."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "",
        editor_widget: QWidget | None = None,
        description: str = "",
        icon: QIcon | None = None,
        reset_button: bool = True,
    ) -> None:
        """
        Args:
            parent: Parent widget.
            title: Text of the first line.
            editor_widget: Widget shown on the right. Can be set later with ``set_editor_widget``.
            description: Smaller text below the title. Hidden while empty.
            icon: Icon shown left of the title. Hidden while null.
            reset_button: Whether the reset button is shown.
        """
        super().__init__(parent)

        self.editor_widget: QWidget | None = None

        self._title_label = QLabel(self)
        self._description_label = QLabel(self)
        self._description_label.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._icon_label = _IconLabel(QIcon(), self)
        self._icon_label.setFixedSize(QSize(16, 16))

        self.btn_reset = QPushButton(self)
        self.btn_reset.setFlat(True)
        self.btn_reset.setToolTip(self.tr("Reset to default value"))
        self.btn_reset.setIcon(get_icon("ArrowReset"))
        self.btn_reset.clicked.connect(self.sig_reset_clicked)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addStretch(1)
        text_layout.addWidget(self._title_label, 0, Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(self._description_label, 0, Qt.AlignmentFlag.AlignLeft)
        text_layout.addStretch(1)

        self._editor_layout = QHBoxLayout()
        self._editor_layout.setContentsMargins(0, 0, 0, 0)
        self._editor_layout.addStretch(1)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        layout.addWidget(self._icon_label)
        layout.addLayout(text_layout, 1)
        layout.addLayout(self._editor_layout, 1)
        layout.addWidget(self.btn_reset)

        # The height comes from the content (fonts, editor), never from a fixed pixel count.
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._apply_fonts()
        self.set_title(title)
        self.set_description(description)
        self.set_icon(icon or QIcon())
        self.set_reset_shown(reset_button)
        if editor_widget is not None:
            self.set_editor_widget(editor_widget)

    def set_editor_widget(self, widget: QWidget | None) -> None:
        """
        Show ``widget`` on the right side of the card.

        A previous editor is taken out of the card and left without a parent, so it is deleted unless the caller
        still holds a reference to it.
        """
        previous = self.editor_widget
        if previous is widget:
            return
        if previous is not None:
            self._editor_layout.removeWidget(previous)
            previous.setParent(None)
        self.editor_widget = widget
        if widget is not None:
            self._editor_layout.addWidget(widget, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def get_title(self) -> str:
        return self._title_label.text()

    @Slot(str)
    def set_title(self, title: str) -> None:
        self._title_label.setText(title)

    def get_description(self) -> str:
        return self._description_label.text()

    @Slot(str)
    def set_description(self, text: str) -> None:
        self._description_label.setText(text)
        self._description_label.setVisible(bool(text))

    def get_icon(self) -> QIcon:
        return self._icon_label.icon

    def set_icon(self, icon: QIcon) -> None:
        self._icon_label.icon = icon
        self._icon_label.setVisible(not icon.isNull())
        self._icon_label.update()

    def get_reset_shown(self) -> bool:
        return not self.btn_reset.isHidden()

    @Slot(bool)
    def set_reset_shown(self, shown: bool) -> None:
        self.btn_reset.setVisible(shown)

    def get_icon_size(self) -> QSize:
        return self._icon_label.size()

    def set_icon_size(self, size: QSize) -> None:
        self._icon_label.setFixedSize(size)

    def _apply_fonts(self) -> None:
        font = self.font()
        self._title_label.setFont(scaled_font(font, _TITLE_FONT_SCALE))
        self._description_label.setFont(scaled_font(font, _DESCRIPTION_FONT_SCALE))

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.FontChange:
            self._apply_fonts()

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self) as painter:
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)
            if is_dark_palette(self.palette()):
                painter.setBrush(QColor(255, 255, 255, 13))
                painter.setPen(QColor(0, 0, 0, 50))
            else:
                painter.setBrush(QColor(255, 255, 255, 170))
                painter.setPen(QColor(0, 0, 0, 19))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    title = Property(str, get_title, set_title)
    description = Property(str, get_description, set_description)
    icon = Property(QIcon, get_icon, set_icon)
    resetShown = Property(bool, get_reset_shown, set_reset_shown)
    iconSize = Property(QSize, get_icon_size, set_icon_size)

    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setTitle = set_title
    setDescription = set_description
    setIcon = set_icon
    setResetShown = set_reset_shown
    setIconSize = set_icon_size
