import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

from ._style_sheets import CARD_STYLE_SHEET
from ._utils import is_dark_theme


class SettingCard(QtWidgets.QFrame):
    """
    A card widget with an icon, title, and text.

    Pretty much taken 1:1 from `qfluentwidgets.SettingCard`, but with some minor tweaks (also to avoid dependency on the
    entire `qfluentwidgets` package).
    """

    sig_reset_clicked: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(
        self,
        title: str,
        editor_widget: QtWidgets.QWidget,
        description: str | None = None,
        icon: QtGui.QIcon | None = None,
        show_reset_button: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._title_label = QtWidgets.QLabel(title, self)
        self._description_label = QtWidgets.QLabel(description or "", self)
        self._icon_label = QtWidgets.QLabel(self)
        self.editor_widget = editor_widget

        self.btn_reset = QtWidgets.QToolButton(self)
        self.btn_reset.setText("Reset")
        self.btn_reset.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.btn_reset.clicked.connect(self.emit_reset_clicked)

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.v_layout = QtWidgets.QVBoxLayout()

        if not description:
            self._description_label.hide()

        if not icon:
            self._icon_label.hide()
        else:
            self._icon_label.setPixmap(icon.pixmap(16, 16))

        if not show_reset_button:
            self.btn_reset.hide()

        self.setFixedHeight(70 if description else 50)

        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(16, 0, 0, 0)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.h_layout.addWidget(self._icon_label, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.h_layout.addSpacing(16)

        self.h_layout.addLayout(self.v_layout)
        self.v_layout.addWidget(self._title_label, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.v_layout.addWidget(self._description_label, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

        self.h_layout.addSpacing(16)

        min_width = max(int(self.width() * 0.25), editor_widget.minimumWidth())
        editor_widget.setMinimumWidth(min_width)
        self.h_layout.addWidget(editor_widget, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.h_layout.addSpacing(8)

        self.h_layout.addWidget(self.btn_reset)
        self.h_layout.addSpacing(16)

        self._description_label.setObjectName("textLabel")

        self.setStyleSheet(CARD_STYLE_SHEET)

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)

    def set_text(self, text: str) -> None:
        self._description_label.setText(text)
        self._description_label.setVisible(bool(text))

    def set_icon(self, icon: QtGui.QIcon) -> None:
        self._icon_label.setPixmap(icon.pixmap(16, 16))

    def set_icon_size(self, size: int) -> None:
        self._icon_label.setFixedSize(size, size)

    def paintEvent(self, arg__1: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)

        if is_dark_theme():
            painter.setBrush(QtGui.QColor(255, 255, 255, 13))
            painter.setPen(QtGui.QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QtGui.QColor(255, 255, 255, 170))
            painter.setPen(QtGui.QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

    @QtCore.Slot()
    def emit_reset_clicked(self) -> None:
        self.sig_reset_clicked.emit()
