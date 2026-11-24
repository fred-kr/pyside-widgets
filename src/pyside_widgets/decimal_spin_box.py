import decimal
import re
from collections.abc import Sequence

from PySide6.QtCore import Property, QSize, Qt, Signal, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox, QStyle, QStyleOptionSpinBox, QWidget

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
    raises; the text is normalized when editing finishes (Return or focus loss).

    The method names mirror ``QDoubleSpinBox``. The setters take ``Decimal``, ``float`` or ``str`` and therefore carry
    no ``@Slot`` decorator; connecting an ``int`` or ``float`` signal to them works as with any Python callable.
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
        line_edit.textChanged.connect(self._on_text_changed)
        # The spin box's own signal fires on Return and on focus loss whatever the text is. The line edit's signal of
        # the same name is withheld while the validator reports Intermediate, e.g. for an out-of-range number.
        self.editingFinished.connect(self._on_editing_finished)
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
        self.updateGeometry()

    def minimum(self) -> decimal.Decimal:
        return self._minimum

    def setMinimum(self, min: _TSupportsDecimal) -> None:
        self._minimum = _to_decimal(min)
        self._maximum = max(self._maximum, self._minimum)
        self._apply_constraints()
        self.updateGeometry()

    def maximum(self) -> decimal.Decimal:
        return self._maximum

    def setMaximum(self, max: _TSupportsDecimal) -> None:
        self._maximum = _to_decimal(max)
        self._minimum = min(self._minimum, self._maximum)
        self._apply_constraints()
        self.updateGeometry()

    def range(self) -> tuple[decimal.Decimal, decimal.Decimal]:
        return self._minimum, self._maximum

    def setRange(self, min: _TSupportsDecimal, max: _TSupportsDecimal) -> None:
        lo, hi = _to_decimal(min), _to_decimal(max)
        if hi < lo:
            lo, hi = hi, lo
        self._minimum, self._maximum = lo, hi
        self._apply_constraints()
        self.updateGeometry()

    def singleStep(self) -> decimal.Decimal:
        return self._single_step

    def setSingleStep(self, val: _TSupportsDecimal) -> None:
        """
        Set the amount one arrow click or key press changes the value by.

        Raises:
            ValueError: If ``val`` is not greater than zero.
        """
        step = _to_decimal(val)
        if step <= 0:
            raise ValueError(f"singleStep must be greater than 0, got {step}")
        self._single_step = step

    def prefix(self) -> str:
        return self._prefix

    def setPrefix(self, prefix: str) -> None:
        self._prefix = prefix
        self._update_display()
        self.updateGeometry()

    def suffix(self) -> str:
        return self._suffix

    def setSuffix(self, suffix: str) -> None:
        self._suffix = suffix
        self._update_display()
        self.updateGeometry()

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

    # Size

    def sizeHint(self) -> QSize:
        return self._hint_for(self.lineEdit().sizeHint().height())

    def minimumSizeHint(self) -> QSize:
        return self._hint_for(self.lineEdit().minimumSizeHint().height())

    def _hint_for(self, height: int) -> QSize:
        """
        Size that fits the wider of the minimum and maximum texts, computed the way ``QDoubleSpinBox`` does it.

        ``QAbstractSpinBox`` cannot do this itself: it does not know the range of a subclass and returns a hint just
        wide enough for the arrow buttons.
        """
        self.ensurePolished()
        metrics = self.fontMetrics()
        affixes = f"{self._prefix}{self._suffix} "
        width = max(
            metrics.horizontalAdvance(self.textFromValue(bound) + affixes) for bound in (self._minimum, self._maximum)
        )
        option = QStyleOptionSpinBox()
        self.initStyleOption(option)
        contents = QSize(width + 2, height)  # 2 px for the text cursor
        return self.style().sizeFromContents(QStyle.ContentsType.CT_SpinBox, option, contents, self)

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

    def _minimum_as_float(self) -> float:
        return float(self._minimum)

    def _maximum_as_float(self) -> float:
        return float(self._maximum)

    def _single_step_as_float(self) -> float:
        return float(self._single_step)

    # Qt properties. The names differ from the accessors above because a Property occupies the class attribute of its
    # own name: a property called "value" would replace the value() method that mirrors QDoubleSpinBox.
    decimalPlaces = Property(int, decimals, setDecimals)
    minimumValue = Property(float, _minimum_as_float, setMinimum)
    maximumValue = Property(float, _maximum_as_float, setMaximum)
    stepSize = Property(float, _single_step_as_float, setSingleStep)
    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setDecimalPlaces = setDecimals
    setMinimumValue = setMinimum
    setMaximumValue = setMaximum
    setStepSize = setSingleStep

    # "QVariant" rather than object, so that Qt can hand over a float, int or str as well as a Decimal.
    # PySide6 accepts the type name as a string; its stubs only declare `type`.
    decimalValue = Property(
        "QVariant",  # pyright: ignore[reportArgumentType]
        value,
        setValue,
        notify=valueChanged,
        user=True,
        designable=False,
    )
