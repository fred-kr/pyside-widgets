"""
ResizableMessageBox: a QDialog-based replacement for QMessageBox that supports resizing, selectable text, the same
standard-button API, and a collapsible detail section for tracebacks or log dumps.
"""

import enum
import traceback

from PySide6.QtCore import Property, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from pyside_widgets._icons import get_icon

QStandardButton = QDialogButtonBox.StandardButton


class ResizableMessageBox(QDialog):
    class Icon(enum.IntEnum):
        NoIcon = 0
        Information = 1
        Warning = 2
        Critical = 3
        Question = 4

    _DETAIL_BTN_SHOW = "Show Details"
    _DETAIL_BTN_HIDE = "Hide Details"
    _STANDARD_PIXMAPS = {
        Icon.Information: QStyle.StandardPixmap.SP_MessageBoxInformation,
        Icon.Warning: QStyle.StandardPixmap.SP_MessageBoxWarning,
        Icon.Critical: QStyle.StandardPixmap.SP_MessageBoxCritical,
        Icon.Question: QStyle.StandardPixmap.SP_MessageBoxQuestion,
    }

    def __init__(
        self,
        icon: int | Icon = Icon.Information,
        title: str = "",
        text: str = "",
        buttons: QStandardButton = QStandardButton.Ok,
        default_button: QStandardButton = QStandardButton.Ok,
        parent: QWidget | None = None,
        min_size: tuple[int, int] = (480, 180),
        selectable_text: bool = True,
        detail_text: str = "",
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(*min_size)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._icon = self.Icon.NoIcon
        self._clicked_button: QStandardButton | None = None

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 12)

        # Top row: icon + message
        top = QHBoxLayout()
        top.setSpacing(12)

        self._icon_label = QLabel()
        self._icon_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        top.addWidget(self._icon_label, 0, Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._text_label = QLabel(text)
        self._text_label.setWordWrap(True)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if selectable_text:
            self._text_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
            )

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(self._text_label)
        inner_layout.addStretch()

        scroll.setWidget(inner)
        top.addWidget(scroll, 1)
        root.addLayout(top, 0)

        # Detail section
        self._detail_widget = self._build_detail_widget()
        self._detail_widget.setVisible(False)
        root.addWidget(self._detail_widget, 1)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.addStretch(1)

        self._detail_toggle = QPushButton(self._DETAIL_BTN_SHOW)
        self._detail_toggle.setIcon(get_icon("MoreHorizontal"))
        self._detail_toggle.setVisible(False)
        self._detail_toggle.clicked.connect(self._toggle_detail)
        btn_row.addWidget(self._detail_toggle, 0)

        self._button_box = QDialogButtonBox(buttons)
        self._button_box.clicked.connect(self._on_button_clicked)
        if default_button:
            btn = self._button_box.button(default_button)
            if btn:
                btn.setDefault(True)
        btn_row.addWidget(self._button_box, 0)

        root.addLayout(btn_row, 0)

        self.set_icon(icon)
        if detail_text:
            self.set_detail_text(detail_text)

    @staticmethod
    def _build_detail_widget() -> QPlainTextEdit:
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editor.setMinimumHeight(120)

        mono = QFont("Monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(9)
        editor.setFont(mono)

        editor.setStyleSheet(
            "QPlainTextEdit {"
            "  border: 1px solid palette(mid);"
            "  border-radius: 4px;"
            "  background: palette(base);"
            "  padding: 6px;"
            "}"
        )
        return editor

    def _toggle_detail(self) -> None:
        visible = not self._detail_widget.isVisible()
        self._detail_widget.setVisible(visible)
        self._detail_toggle.setText(self._DETAIL_BTN_HIDE if visible else self._DETAIL_BTN_SHOW)
        extra = max(200, self._detail_widget.minimumHeight() + 24)
        if not visible:
            extra = -extra
        self.resize(self.width(), self.height() + extra)

    def _on_button_clicked(self, button: QAbstractButton) -> None:
        self._clicked_button = self._button_box.standardButton(button)
        self.done(self._clicked_button.value)

    def reject(self) -> None:
        """Escape closes the dialog as if Cancel was clicked (or with ``NoButton`` if there is no Cancel)."""
        if self._clicked_button is None:
            buttons = self._button_box.standardButtons()
            cancel = QStandardButton.Cancel
            self._clicked_button = cancel if buttons & cancel else QStandardButton.NoButton
        self.done(self._clicked_button.value)

    # Public API

    def get_icon(self) -> int:
        return int(self._icon)

    def set_icon(self, icon: int | Icon) -> None:
        self._icon = self.Icon(int(icon))
        pixmap = self._STANDARD_PIXMAPS.get(self._icon)
        if pixmap is None:
            self._icon_label.setVisible(False)
            return
        self._icon_label.setPixmap(self.style().standardIcon(pixmap, None, self).pixmap(QSize(48, 48)))
        self._icon_label.setVisible(True)

    def get_text(self) -> str:
        return self._text_label.text()

    def set_text(self, text: str) -> None:
        self._text_label.setText(text)

    def get_detail_text(self) -> str:
        return self._detail_widget.toPlainText()

    def set_detail_text(self, text: str) -> None:
        """Set the raw detail text (stacktrace, log dump, etc.). The toggle button is shown when text is non-empty."""
        self._detail_widget.setPlainText(text)
        self._detail_toggle.setVisible(bool(text))

    def set_exception(self, exc: BaseException) -> None:
        """Show the formatted traceback of ``exc`` in the detail section."""
        self.set_detail_text("".join(traceback.format_exception(exc)))

    def clicked_button(self) -> QStandardButton | None:
        """The standard button that closed the dialog, or None while it is still open."""
        return self._clicked_button

    def button_box(self) -> QDialogButtonBox:
        return self._button_box

    icon = Property(int, get_icon, set_icon)
    text = Property(str, get_text, set_text)
    detail_text = Property(str, get_detail_text, set_detail_text)

    # Static convenience methods; each returns the clicked standard button as an int, like QMessageBox.

    @staticmethod
    def information(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: QStandardButton = QStandardButton.Ok,
        detail: str = "",
    ) -> int:
        return ResizableMessageBox(
            ResizableMessageBox.Icon.Information, title, text, buttons, parent=parent, detail_text=detail
        ).exec()

    @staticmethod
    def warning(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: QStandardButton = QStandardButton.Ok | QStandardButton.Cancel,
        detail: str = "",
    ) -> int:
        return ResizableMessageBox(
            ResizableMessageBox.Icon.Warning, title, text, buttons, parent=parent, detail_text=detail
        ).exec()

    @staticmethod
    def critical(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: QStandardButton = QStandardButton.Ok,
        detail: str = "",
    ) -> int:
        return ResizableMessageBox(
            ResizableMessageBox.Icon.Critical, title, text, buttons, parent=parent, detail_text=detail
        ).exec()

    @staticmethod
    def question(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: QStandardButton = QStandardButton.Yes | QStandardButton.No,
        detail: str = "",
    ) -> int:
        return ResizableMessageBox(
            ResizableMessageBox.Icon.Question, title, text, buttons, parent=parent, detail_text=detail
        ).exec()

    @staticmethod
    def from_exception(
        parent: QWidget | None,
        title: str,
        text: str,
        exc: BaseException,
        buttons: QStandardButton = QStandardButton.Ok,
    ) -> int:
        """Critical dialog pre-loaded with the formatted traceback of ``exc``."""
        dialog = ResizableMessageBox(ResizableMessageBox.Icon.Critical, title, text, buttons, parent=parent)
        dialog.set_exception(exc)
        return dialog.exec()
