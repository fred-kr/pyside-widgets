"""
ResizableMessageBox: a QDialog-based replacement for QMessageBox that supports resizing, selectable text, the same
standard-button API, and a collapsible detail section for tracebacks or log dumps.
"""

import traceback

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from pyside_widgets._icons import get_icon

type Buttons = QMessageBox.StandardButton | QDialogButtonBox.StandardButton
"""
Standard buttons of either Qt class. The two enums have the same members and values but never compare equal to each
other, so the dialog accepts both and always answers with ``QMessageBox.StandardButton``.
"""

_STANDARD_PIXMAPS = {
    QMessageBox.Icon.Information: QStyle.StandardPixmap.SP_MessageBoxInformation,
    QMessageBox.Icon.Warning: QStyle.StandardPixmap.SP_MessageBoxWarning,
    QMessageBox.Icon.Critical: QStyle.StandardPixmap.SP_MessageBoxCritical,
    QMessageBox.Icon.Question: QStyle.StandardPixmap.SP_MessageBoxQuestion,
}


def _box_buttons(buttons: Buttons) -> QDialogButtonBox.StandardButton:
    return QDialogButtonBox.StandardButton(buttons.value)


class ResizableMessageBox(QDialog):
    """
    Message dialog with the constructor and static helpers of ``QMessageBox``.

    The static helpers return the clicked ``QMessageBox.StandardButton``, so code written for ``QMessageBox`` keeps
    working:

        if ResizableMessageBox.question(window, "Save", "Save changes?") == QMessageBox.StandardButton.Yes:
            save()
    """

    Icon = QMessageBox.Icon
    StandardButton = QMessageBox.StandardButton

    def __init__(
        self,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
        title: str = "",
        text: str = "",
        buttons: Buttons = QMessageBox.StandardButton.Ok,
        default_button: Buttons = QMessageBox.StandardButton.Ok,
        parent: QWidget | None = None,
        *,
        min_size: tuple[int, int] = (480, 180),
        selectable_text: bool = True,
        detail_text: str = "",
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(*min_size)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._icon = QMessageBox.Icon.NoIcon
        self._clicked_button: QMessageBox.StandardButton | None = None

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

        self._detail_toggle = QPushButton(self.tr("Show Details"))
        self._detail_toggle.setIcon(get_icon("MoreHorizontal"))
        self._detail_toggle.setVisible(False)
        self._detail_toggle.clicked.connect(self._toggle_detail)
        btn_row.addWidget(self._detail_toggle, 0)

        self._button_box = QDialogButtonBox(_box_buttons(buttons))
        self._button_box.clicked.connect(self._on_button_clicked)
        default = self._button_box.button(_box_buttons(default_button))
        if default is not None:
            default.setDefault(True)
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
        editor.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        return editor

    @Slot()
    def _toggle_detail(self) -> None:
        visible = not self._detail_widget.isVisible()
        self._detail_widget.setVisible(visible)
        self._detail_toggle.setText(self.tr("Hide Details") if visible else self.tr("Show Details"))
        extra = max(200, self._detail_widget.minimumHeight() + 24)
        if not visible:
            extra = -extra
        self.resize(self.width(), self.height() + extra)

    @Slot(QAbstractButton)
    def _on_button_clicked(self, button: QAbstractButton) -> None:
        self._clicked_button = QMessageBox.StandardButton(self._button_box.standardButton(button).value)
        self.done(self._clicked_button.value)

    def reject(self) -> None:
        """Escape closes the dialog as if Cancel was clicked (or with ``NoButton`` if there is no Cancel)."""
        if self._clicked_button is None:
            has_cancel = bool(self._button_box.standardButtons() & QDialogButtonBox.StandardButton.Cancel)
            self._clicked_button = (
                QMessageBox.StandardButton.Cancel if has_cancel else QMessageBox.StandardButton.NoButton
            )
        self.done(self._clicked_button.value)

    # Public API

    def get_icon(self) -> QMessageBox.Icon:
        return self._icon

    def set_icon(self, icon: QMessageBox.Icon) -> None:
        self._icon = icon
        standard_pixmap = _STANDARD_PIXMAPS.get(icon)
        if standard_pixmap is None:
            self._icon_label.setVisible(False)
            return
        style = self.style()
        extent = style.pixelMetric(QStyle.PixelMetric.PM_MessageBoxIconSize, None, self)
        standard_icon = style.standardIcon(standard_pixmap, None, self)
        self._icon_label.setPixmap(standard_icon.pixmap(QSize(extent, extent), self.devicePixelRatioF()))
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

    def clicked_button(self) -> QMessageBox.StandardButton | None:
        """The standard button that closed the dialog, or None while it is still open."""
        return self._clicked_button

    def button_box(self) -> QDialogButtonBox:
        return self._button_box

    # Static convenience methods; each returns the clicked standard button, like the QMessageBox ones.

    @staticmethod
    def _run(
        icon: QMessageBox.Icon,
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: Buttons,
        detail: str = "",
        exc: BaseException | None = None,
    ) -> QMessageBox.StandardButton:
        dialog = ResizableMessageBox(icon, title, text, buttons, parent=parent, detail_text=detail)
        if exc is not None:
            dialog.set_exception(exc)
        return QMessageBox.StandardButton(dialog.exec())

    @staticmethod
    def information(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: Buttons = QMessageBox.StandardButton.Ok,
        detail: str = "",
    ) -> QMessageBox.StandardButton:
        return ResizableMessageBox._run(QMessageBox.Icon.Information, parent, title, text, buttons, detail)

    @staticmethod
    def warning(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: Buttons = QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        detail: str = "",
    ) -> QMessageBox.StandardButton:
        return ResizableMessageBox._run(QMessageBox.Icon.Warning, parent, title, text, buttons, detail)

    @staticmethod
    def critical(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: Buttons = QMessageBox.StandardButton.Ok,
        detail: str = "",
    ) -> QMessageBox.StandardButton:
        return ResizableMessageBox._run(QMessageBox.Icon.Critical, parent, title, text, buttons, detail)

    @staticmethod
    def question(
        parent: QWidget | None,
        title: str,
        text: str,
        buttons: Buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        detail: str = "",
    ) -> QMessageBox.StandardButton:
        return ResizableMessageBox._run(QMessageBox.Icon.Question, parent, title, text, buttons, detail)

    @staticmethod
    def from_exception(
        parent: QWidget | None,
        title: str,
        text: str,
        exc: BaseException,
        buttons: Buttons = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """Critical dialog pre-loaded with the formatted traceback of ``exc``."""
        return ResizableMessageBox._run(QMessageBox.Icon.Critical, parent, title, text, buttons, exc=exc)
