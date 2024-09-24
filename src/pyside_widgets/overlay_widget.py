from PySide6 import QtCore, QtGui, QtWidgets


class OverlayWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self._target = parent

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        self._content = QtWidgets.QWidget()
        self._content.setStyleSheet("background: rgba(0, 0, 0, 0);")

        font = self._content.font()
        font.setPointSize(28)
        font.setWeight(QtGui.QFont.Weight.DemiBold)

        self._text = QtWidgets.QLabel("Running...")
        self._text.setStyleSheet("background: transparent; color: white;")
        self._text.setFont(font)
        self._text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._spinner = QtWidgets.QProgressBar()
        self._spinner.setRange(0, 0)

        self._layout_content = QtWidgets.QVBoxLayout()
        self._layout_content.setContentsMargins(0, 0, 0, 0)
        self._layout_content.setSpacing(12)

        self._layout_content.addWidget(
            self._text,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self._layout_content.addWidget(
            self._spinner,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )

        self._content.setLayout(self._layout_content)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(
            self._content,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )

        self.setLayout(self._layout)

    def set_text(self, text: str) -> None:
        self._text.setText(text)

    def show_overlay(self, text: str | None = None) -> None:
        self._target.setEnabled(False)

        if text is not None:
            self._text.setText(text)

        self.setGeometry(self._target.geometry())
        self.move(0, 0)
        self.raise_()
        self.show()

    def hide_overlay(self) -> None:
        self._target.setEnabled(True)
        self.hide()
