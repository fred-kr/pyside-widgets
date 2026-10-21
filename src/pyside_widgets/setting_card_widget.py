from typing import Any

from PySide6.QtCore import Property, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QIcon, QPainter, QPaintEvent, QPalette
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from pyside_widgets._icons import get_icon
from pyside_widgets._style_sheets import CARD_STYLE_SHEET
from pyside_widgets._utils import NOTHING


class PlaceholderWidget(QFrame):
    """Stand-in editor shown by ``SettingCard`` when no editor widget is given."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)

        self.label = QLabel("Placeholder", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def setPlaceholderText(self, text: str) -> None:
        self.label.setText(text)


class SettingCard(QFrame):
    """
    A card with an icon, title, description, an editor widget and a reset button.

    Modelled on ``qfluentwidgets.SettingCard`` without the qfluentwidgets dependency. Colors follow the widget palette,
    so the card works in light and dark themes.
    """

    sig_reset_clicked = Signal()

    def __init__(
        self,
        title: str = "",
        editor_widget: QWidget | None = None,
        default_value: Any = NOTHING,
        set_value_name: str | None = None,
        description: str = "",
        icon: QIcon | None = None,
        reset_button: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.p_title = title
        self.p_description = description
        self.p_icon = icon or QIcon()
        self.p_icon_size = QSize(16, 16)
        self.p_reset_button = reset_button

        if editor_widget is None:
            editor_widget = PlaceholderWidget()
            if default_value is NOTHING:
                default_value = "Default Value"
            set_value_name = set_value_name or "setPlaceholderText"
        self.editor_widget = editor_widget
        self._default_value = default_value
        self._set_value_name = set_value_name

        self._title_label = QLabel(self.p_title, self)
        self._description_label = QLabel(self.p_description, self)
        self._description_label.setObjectName("textLabel")  # targeted by CARD_STYLE_SHEET
        self._description_label.setForegroundRole(QPalette.ColorRole.PlaceholderText)
        self._icon_label = QLabel(self)

        self.btn_reset = QPushButton(self)
        self.btn_reset.setFlat(True)
        self.btn_reset.setToolTip("Reset to default value")
        self.btn_reset.setIcon(get_icon("ArrowReset"))
        self.btn_reset.clicked.connect(self._on_reset_clicked)

        self.h_layout = QHBoxLayout(self)
        self.v_layout = QVBoxLayout()

        if not self.p_description:
            self._description_label.hide()

        if self.p_icon.isNull():
            self._icon_label.hide()
        else:
            self._icon_label.setPixmap(self.p_icon.pixmap(self.p_icon_size))

        if not self.p_reset_button:
            self.btn_reset.hide()

        self.setFixedHeight(70 if self.p_description else 50)

        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(16, 0, 0, 0)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.h_layout.addWidget(self._icon_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.h_layout.addSpacing(16)

        self.h_layout.addLayout(self.v_layout, 1)
        self.v_layout.addWidget(self._title_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.v_layout.addWidget(self._description_label, 0, Qt.AlignmentFlag.AlignLeft)

        self.h_layout.addSpacing(16)

        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addStretch(1)
        editor_layout.addWidget(self.editor_widget, 1, Qt.AlignmentFlag.AlignRight)

        self.h_layout.addLayout(editor_layout, 1)
        self.h_layout.addSpacing(8)

        self.h_layout.addWidget(self.btn_reset)
        self.h_layout.addSpacing(16)

        self.setStyleSheet(CARD_STYLE_SHEET)

    def get_title(self) -> str:
        return self.p_title

    def set_title(self, title: str) -> None:
        self.p_title = title
        self._title_label.setText(title)

    def get_description(self) -> str:
        return self.p_description

    def set_description(self, text: str) -> None:
        self.p_description = text
        self.setFixedHeight(70 if text else 50)
        self._description_label.setText(text)
        self._description_label.setVisible(bool(text))

    def get_icon(self) -> QIcon:
        return self.p_icon

    def set_icon(self, icon: QIcon) -> None:
        self.p_icon = icon
        if icon.isNull():
            self._icon_label.hide()
            return
        self._icon_label.setPixmap(icon.pixmap(self.p_icon_size))
        self._icon_label.show()

    def get_reset_shown(self) -> bool:
        return self.p_reset_button

    def set_reset_shown(self, shown: bool) -> None:
        self.p_reset_button = shown
        self.btn_reset.setVisible(shown)

    def get_icon_size(self) -> QSize:
        return self.p_icon_size

    def set_icon_size(self, size: QSize) -> None:
        self.p_icon_size = size
        self._icon_label.setFixedSize(size)
        if not self.p_icon.isNull():
            self._icon_label.setPixmap(self.p_icon.pixmap(size))

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        is_dark = self.palette().color(QPalette.ColorRole.Window).lightness() < 128
        if is_dark:
            painter.setBrush(QColor(255, 255, 255, 13))
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    @Slot()
    def _on_reset_clicked(self) -> None:
        """Emit ``sig_reset_clicked`` and, if a default value and setter name were given, apply the default."""
        self.sig_reset_clicked.emit()
        if self._default_value is NOTHING or not self._set_value_name:
            return
        getattr(self.editor_widget, self._set_value_name)(self._default_value)

    title = Property(str, get_title, set_title)
    description = Property(str, get_description, set_description)
    icon = Property(QIcon, get_icon, set_icon)
    reset_shown = Property(bool, get_reset_shown, set_reset_shown)
    icon_size = Property(QSize, get_icon_size, set_icon_size)
