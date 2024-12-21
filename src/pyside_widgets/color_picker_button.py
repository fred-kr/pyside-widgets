from PySide6 import QtCore, QtGui, QtWidgets


class ColorPickerButton(QtWidgets.QPushButton):
    """
    A button that opens a color picker dialog when clicked.
    """

    sig_color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color: QtGui.QColor | None = None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._default_color = self.palette().color(QtGui.QPalette.ColorRole.Base)
        self._color = color or self._default_color
        self._show_alpha = False

        self.set_color(self._color)
        self.pressed.connect(self._on_clicked)

    @property
    def text_fmt(self) -> QtGui.QColor.NameFormat:
        """Returns the appropriate color name format based on the visibility of the alpha channel."""
        return QtGui.QColor.NameFormat.HexArgb if self._show_alpha else QtGui.QColor.NameFormat.HexRgb

    def set_show_alpha(self, value: bool) -> None:
        """Controls the visibility of the alpha channel in the color picker.

        Determines whether the alpha (transparency) component will be displayed in the color selection interface.

        Args:
            value: A boolean flag indicating whether to show the alpha channel.
        """
        self._show_alpha = value
        self.set_color(self._color)

    def set_color(self, color: QtGui.QColor) -> None:
        """Sets the current color of the button.

        Emits `sig_color_changed` if the color actually changes.

        Args:
            color: The new color to set.
        """
        if not color.isValid():
            return

        if color != self._color:
            self._color = color
            self.sig_color_changed.emit(self._color)

        self.setText(self._color.name(self.text_fmt))
        text_color = (
            self.palette().color(QtGui.QPalette.ColorRole.Text)
            if self._color.lightness() > 128
            else self.palette().color(QtGui.QPalette.ColorRole.BrightText)
        )
        self.setStyleSheet(
            f"ColorPickerButton {{ background-color: {self._color.name()}; color: {text_color.name()}; }}"
        )

    def color(self) -> QtGui.QColor:
        return self._color

    @QtCore.Slot()
    def _on_clicked(self) -> None:
        """Launches a color selection dialog when the button is clicked.

        Allows the user to choose a new color with optional alpha channel visibility based on configuration.
        """
        if self._show_alpha:
            new_color = QtWidgets.QColorDialog.getColor(
                self._color, self, options=QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel
            )
        else:
            new_color = QtWidgets.QColorDialog.getColor(self._color, self)
        self.set_color(new_color)
