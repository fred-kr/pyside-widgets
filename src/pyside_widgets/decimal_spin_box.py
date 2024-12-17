import decimal
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

D = decimal.Decimal
type _TSupportsDecimal = decimal.Decimal | float | str | tuple[int, t.Sequence[int], int]


class DecimalSpinBox(QtWidgets.QAbstractSpinBox):
    valueChanged: t.ClassVar[QtCore.Signal] = QtCore.Signal(decimal.Decimal)
    textChanged: t.ClassVar[QtCore.Signal] = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._decimal_places: int = 2
        self._value: decimal.Decimal = D("0.00")
        self._step: decimal.Decimal = D("1.00")
        self._minimum: decimal.Decimal = D("-9999999.99")
        self._maximum: decimal.Decimal = D("9999999.99")
        self._prefix: str = ""
        self._suffix: str = ""
        self.setDecimals(self._decimal_places)
        self.lineEdit().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.lineEdit().setText(self._formatted_value())
        self.lineEdit().editingFinished.connect(self._on_editing_finished)
        self.lineEdit().textChanged.connect(self._on_text_changed)

    def setDecimals(self, prec: int) -> None:
        """Sets the number of decimal places to display."""
        self._decimal_places = prec
        self._updateDisplay()

    def minimum(self) -> decimal.Decimal:
        """Returns the current minimum value."""
        return self._minimum

    def setMinimum(self, min: _TSupportsDecimal) -> None:
        """Sets the minimum value."""
        self._minimum = D(min)
        self._updateDisplay()

    def maximum(self) -> decimal.Decimal:
        """Returns the current maximum value."""
        return self._maximum

    def setMaximum(self, max: _TSupportsDecimal) -> None:
        """Sets the maximum value."""
        self._maximum = D(max)
        self._updateDisplay()

    def range(self) -> tuple[decimal.Decimal, decimal.Decimal]:
        """Returns the minimum and maximum values."""
        return self._minimum, self._maximum

    def setRange(self, min: _TSupportsDecimal, max: _TSupportsDecimal) -> None:
        """Sets the minimum and maximum values."""
        self._minimum = D(min)
        self._maximum = D(max)
        self._updateDisplay()

    def setSingleStep(self, val: _TSupportsDecimal) -> None:
        """Sets the step size for each increment/decrement."""
        self._step = D(val)

    def setPrefix(self, prefix: str) -> None:
        """Set the prefix to display before the value."""
        self._prefix = prefix
        self._updateDisplay()

    def setSuffix(self, suffix: str) -> None:
        """Set the suffix to display after the value."""
        self._suffix = suffix
        self._updateDisplay()

    def value(self) -> decimal.Decimal:
        """Returns the current value as a Decimal."""
        return self._value

    def setValue(self, value: _TSupportsDecimal) -> None:
        """Sets the current value, ensuring it is within range."""
        value = D(value)
        if value < self._minimum:
            value = self._minimum
        elif value > self._maximum:
            value = self._maximum
        new_value = value.quantize(D("1." + "0" * self._decimal_places))
        if new_value != self._value:
            self._value = new_value
            self.valueChanged.emit(self._value)
            self._updateDisplay()

    def stepBy(self, steps: int) -> None:
        """Handles stepping the value up or down by the defined step size."""
        new_value = self._value + (self._step * steps)
        self.setValue(new_value)

    @QtCore.Slot()
    def _on_editing_finished(self) -> None:
        """Handles the editing finished event to update the value from the text."""
        try:
            value = D(self.lineEdit().text().replace(self._prefix, "").replace(self._suffix, "").strip())
            self.setValue(value)
        except Exception:
            self._updateDisplay()  # Reset to last valid value if input is invalid

    @QtCore.Slot(str)
    def _on_text_changed(self, text: str) -> None:
        """Handles the text changed event to mimic `QDoubleSpinBox.textChanged`."""
        full_text = f"{self._prefix}{text}{self._suffix}"
        self.textChanged.emit(full_text)

    def _updateDisplay(self) -> None:
        """Updates the displayed value."""
        self.lineEdit().setText(self._formatted_value())

    def _formatted_value(self) -> str:
        """Formats the current value for display, including the prefix and suffix."""
        return f"{self._prefix}{self._value:.{self._decimal_places}f}{self._suffix}"

    def validate(self, input: str, pos: int) -> tuple[QtGui.QValidator.State, str, int]:
        """Validates the input string."""
        try:
            D(input.replace(self._prefix, "").replace(self._suffix, "").strip())
            return QtGui.QValidator.State.Acceptable, input, pos
        except Exception:
            return QtGui.QValidator.State.Invalid, input, pos

    def stepEnabled(self) -> QtWidgets.QAbstractSpinBox.StepEnabledFlag:
        """Determines which steps buttons should be enabled."""
        if self._value <= self._minimum:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        elif self._value >= self._maximum:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        else:
            return (
                QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
                | QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
            )

    def textFromValue(self, value: decimal.Decimal) -> str:
        """Returns the text representation of the given value."""
        return str(value)

    def valueFromText(self, text: str) -> decimal.Decimal:
        """Returns the value represented by the given text."""
        return D(text)
