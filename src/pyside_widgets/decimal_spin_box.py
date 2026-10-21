import decimal
import re
from collections.abc import Sequence

from PySide6.QtCore import Property, Qt, Signal, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox, QWidget

D = decimal.Decimal
type _TSupportsDecimal = decimal.Decimal | float | str | tuple[int, Sequence[int], int]

_PARTIAL_NUMBER = re.compile(r"[+-]?(\d+\.?\d*|\.\d*)?")
"""Text that can still become a valid number with more typing: "", "-", "1.", ".5"."""


def _to_decimal(value: _TSupportsDecimal) -> decimal.Decimal:
    # Going through str() keeps floats like 0.1 as Decimal("0.1") rather than their binary expansion.
    return D(str(value)) if isinstance(value, float) else D(value)


class DecimalSpinBox(QAbstractSpinBox):
    """
    Spin box that stores its value as ``decimal.Decimal``.

    Values are clamped to ``[minimum, maximum]`` and rounded to ``decimals`` places. Partial input while typing never
    raises; the text is normalized when editing finishes.
    """

    valueChanged = Signal(decimal.Decimal)
    textChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._decimal_places: int = 2
        self._value: decimal.Decimal = D("1.00")
        self._single_step: decimal.Decimal = D("1.00")
        self._minimum: decimal.Decimal = D("0.00")
        self._maximum: decimal.Decimal = D("99.99")
        self._prefix: str = ""
        self._suffix: str = ""

        line_edit = self.lineEdit()
        line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        line_edit.editingFinished.connect(self._on_editing_finished)
        line_edit.textChanged.connect(self._on_text_changed)
        self.setKeyboardTracking(True)
        self._update_display()

    # Precision and range

    def decimals(self) -> int:
        """Number of decimal places the value is rounded to and displayed with."""
        return self._decimal_places

    def setDecimals(self, prec: int) -> None:
        self._decimal_places = max(0, prec)
        self._apply_constraints()
        self._update_display()

    def minimum(self) -> decimal.Decimal:
        return self._minimum

    def f_minimum(self) -> float:
        return float(self._minimum)

    def setMinimum(self, min: _TSupportsDecimal) -> None:
        self._minimum = _to_decimal(min)
        self._maximum = max(self._maximum, self._minimum)
        self._apply_constraints()

    def maximum(self) -> decimal.Decimal:
        return self._maximum

    def f_maximum(self) -> float:
        return float(self._maximum)

    def setMaximum(self, max: _TSupportsDecimal) -> None:
        self._maximum = _to_decimal(max)
        self._minimum = min(self._minimum, self._maximum)
        self._apply_constraints()

    def range(self) -> tuple[decimal.Decimal, decimal.Decimal]:
        return self._minimum, self._maximum

    def setRange(self, min: _TSupportsDecimal, max: _TSupportsDecimal) -> None:
        lo, hi = _to_decimal(min), _to_decimal(max)
        if hi < lo:
            lo, hi = hi, lo
        self._minimum, self._maximum = lo, hi
        self._apply_constraints()

    def singleStep(self) -> decimal.Decimal:
        return self._single_step

    def f_singleStep(self) -> float:
        return float(self._single_step)

    def setSingleStep(self, val: _TSupportsDecimal) -> None:
        self._single_step = _to_decimal(val)

    def prefix(self) -> str:
        return self._prefix

    def setPrefix(self, prefix: str) -> None:
        self._prefix = prefix
        self._update_display()

    def suffix(self) -> str:
        return self._suffix

    def setSuffix(self, suffix: str) -> None:
        self._suffix = suffix
        self._update_display()

    # Value

    def value(self) -> decimal.Decimal:
        return self._value

    def intValue(self) -> int:
        return int(self._value)

    def floatValue(self) -> float:
        return float(self._value)

    def setValue(self, value: _TSupportsDecimal) -> None:
        """Set the value, clamped to the range and rounded to ``decimals`` places. Emits ``valueChanged`` on change."""
        self._set_value(_to_decimal(value), update_display=True)

    def _set_value(self, value: decimal.Decimal, update_display: bool) -> None:
        new_value = self._normalize(value)
        if new_value == self._value:
            return
        self._value = new_value
        self.valueChanged.emit(new_value)
        if update_display:
            self._update_display()

    def _normalize(self, value: decimal.Decimal) -> decimal.Decimal:
        value = min(max(value, self._minimum), self._maximum)
        return value.quantize(D(1).scaleb(-self._decimal_places), rounding=decimal.ROUND_HALF_UP)

    def _apply_constraints(self) -> None:
        """Re-clamp and re-round the current value after a range or precision change."""
        self._set_value(self._value, update_display=True)

    def stepBy(self, steps: int) -> None:
        self.setValue(self._value + self._single_step * steps)

    def stepEnabled(self) -> QAbstractSpinBox.StepEnabledFlag:
        flags = QAbstractSpinBox.StepEnabledFlag.StepNone
        if self._value > self._minimum:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        if self._value < self._maximum:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        return flags

    # Text

    def _strip_affixes(self, text: str) -> str:
        return text.strip().removeprefix(self._prefix).removesuffix(self._suffix).strip()

    def _parse(self, text: str) -> decimal.Decimal | None:
        """Decimal value of ``text`` (prefix/suffix allowed), or None if it is not a finite number."""
        try:
            value = D(self._strip_affixes(text))
        except decimal.InvalidOperation:
            return None
        return value if value.is_finite() else None

    def textFromValue(self, value: decimal.Decimal) -> str:
        return f"{value:.{self._decimal_places}f}"

    def valueFromText(self, text: str) -> decimal.Decimal:
        parsed = self._parse(text)
        return self._value if parsed is None else parsed

    def validate(self, input: str, pos: int) -> tuple[QValidator.State, str, int]:
        parsed = self._parse(input)
        if parsed is not None and self._minimum <= parsed <= self._maximum:
            return QValidator.State.Acceptable, input, pos
        if parsed is not None or _PARTIAL_NUMBER.fullmatch(self._strip_affixes(input)):
            return QValidator.State.Intermediate, input, pos
        return QValidator.State.Invalid, input, pos

    def _formatted_value(self) -> str:
        return f"{self._prefix}{self.textFromValue(self._value)}{self._suffix}"

    def _update_display(self) -> None:
        self.lineEdit().setText(self._formatted_value())

    @Slot()
    def _on_editing_finished(self) -> None:
        parsed = self._parse(self.lineEdit().text())
        if parsed is not None:
            out_of_range = not (self._minimum <= parsed <= self._maximum)
            keep_previous = self.correctionMode() == QAbstractSpinBox.CorrectionMode.CorrectToPreviousValue
            if not (out_of_range and keep_previous):
                self.setValue(parsed)
        self._update_display()

    @Slot(str)
    def _on_text_changed(self, text: str) -> None:
        self.textChanged.emit(text)
        if not self.keyboardTracking():
            return
        parsed = self._parse(text)
        if parsed is not None:
            # Keep the user's text while typing; editingFinished normalizes it.
            self._set_value(parsed, update_display=False)

    # Qt properties for Designer. Names differ from the Python accessors because a Property would shadow them.
    decimalPlaces = Property(int, decimals, setDecimals)
    minimumValue = Property(float, f_minimum, setMinimum)
    maximumValue = Property(float, f_maximum, setMaximum)
    stepSize = Property(float, f_singleStep, setSingleStep)
