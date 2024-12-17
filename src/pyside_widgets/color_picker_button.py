from PySide6 import QtCore, QtGui, QtWidgets


class ColorPickerButton(QtWidgets.QPushButton):
    """
    A button that opens a color picker dialog when clicked.
    """

    sig_color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color: QtGui.QColor | None = None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ColorPickerButton")

        self._color: QtGui.QColor | None = None
        self._default_color = QtGui.QColor("lightgray")

        self.setToolTip("Click to change color")

        self.pressed.connect(self._on_clicked)

        self.set_color(self._default_color)

    def set_color(self, color: QtGui.QColor | None) -> None:
        if color and color != self._color:
            self._color = color
            self.setText(self._color.name())
            self.sig_color_changed.emit(color)

        if self._color:
            if self._color.lightness() < 128:
                self.setStyleSheet(f"#{self.objectName()} {{ background-color: {self._color.name()}; color: white; }}")
            else:
                self.setStyleSheet(f"#{self.objectName()} {{ background-color: {self._color.name()}; color: black; }}")
        else:
            self.setStyleSheet(
                f"#{self.objectName()} {{ background-color: {self._default_color.name()}; color: black; }}"
            )

    def color(self) -> QtGui.QColor | None:
        return self._color

    @QtCore.Slot()
    def _on_clicked(self) -> None:
        """
        Show color-picker dialog.
        """
        dlg = QtWidgets.QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(self._color)
        if dlg.exec():
            self.set_color(dlg.currentColor())
