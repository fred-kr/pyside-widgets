import decimal

from PySide6 import QtCore, QtGui, QtWidgets

D = decimal.Decimal


class DecimalSpinBox(QtWidgets.QAbstractSpinBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.decimal_places: int = 2
        self._value: decimal.Decimal = D("0.00")
        self._step: decimal.Decimal = D("1.00")
        self.minimum: decimal.Decimal = D("-9999999.99")
        self.maximum: decimal.Decimal = D("9999999.99")
        self.setDecimals(self.decimal_places)
        self.lineEdit().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.lineEdit().setText(self._formatted_value())
        self.lineEdit().editingFinished.connect(self._on_editing_finished)

    def setDecimals(self, prec: int) -> None:
        """Sets the number of decimal places to display."""
        self.decimal_places = prec
        self._updateDisplay()

    def setRange(self, min: decimal.Decimal, max: decimal.Decimal) -> None:
        """Sets the minimum and maximum values."""
        self.minimum = D(min)
        self.maximum = D(max)
        self._updateDisplay()

    def setSingleStep(self, val: decimal.Decimal) -> None:
        """Sets the step size for each increment/decrement."""
        self._step = D(val)

    def value(self) -> decimal.Decimal:
        """Returns the current value as a Decimal."""
        return self._value

    def setValue(self, value: decimal.Decimal) -> None:
        """Sets the current value, ensuring it is within range."""
        value = D(value)
        if value < self.minimum:
            value = self.minimum
        elif value > self.maximum:
            value = self.maximum
        self._value = value.quantize(D("1." + "0" * self.decimal_places))
        self._updateDisplay()

    def stepBy(self, steps: int) -> None:
        """Handles stepping the value up or down by the defined step size."""
        new_value = self._value + (self._step * steps)
        self.setValue(new_value)

    @QtCore.Slot()
    def _on_editing_finished(self) -> None:
        """Handles the editing finished event to update the value from the text."""
        try:
            value = D(self.lineEdit().text())
            self.setValue(value)
        except Exception:
            self._updateDisplay()

    def _updateDisplay(self) -> None:
        """Updates the displayed value."""
        self.lineEdit().setText(self._formatted_value())

    def _formatted_value(self) -> str:
        """Formats the current value for display."""
        return f"{self._value:.{self.decimal_places}f}"

    def validate(self, input: str, pos: int) -> tuple[QtGui.QValidator.State, str, int]:
        """Validates the input string."""
        try:
            D(input)
            return QtGui.QValidator.State.Acceptable, input, pos
        except Exception:
            return QtGui.QValidator.State.Invalid, input, pos

    def stepEnabled(self) -> QtWidgets.QAbstractSpinBox.StepEnabledFlag:
        """Determines which steps buttons should be enabled."""
        if self._value <= self.minimum:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        elif self._value >= self.maximum:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        else:
            return (
                QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
                | QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
            )
