from decimal import Decimal

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox, QDoubleSpinBox, QLineEdit, QVBoxLayout, QWidget

from pyside_widgets.decimal_spin_box import DecimalSpinBox


@pytest.fixture
def spin_box(qtbot) -> DecimalSpinBox:
    widget = DecimalSpinBox()
    qtbot.addWidget(widget)
    widget.setRange(0, 100)
    widget.setDecimals(2)
    widget.setValue(10)
    return widget


def _type(qtbot, spin_box: DecimalSpinBox, text: str) -> None:
    """Replace the whole text through key events, the way a user does."""
    spin_box.selectAll()
    qtbot.keyClicks(spin_box, text)


def test_value_is_decimal_and_display_is_formatted(spin_box: DecimalSpinBox):
    assert spin_box.value() == Decimal("10.00")
    assert spin_box.lineEdit().text() == "10.00"
    assert spin_box.intValue() == 10
    assert spin_box.floatValue() == 10.0


def test_float_input_does_not_leak_binary_expansion(spin_box: DecimalSpinBox):
    spin_box.setDecimals(4)
    spin_box.setValue(0.1)
    assert spin_box.value() == Decimal("0.1000")


@pytest.mark.parametrize("text", ["", "-", ".", "+", "abc", "1e", "nan"])
def test_partial_or_invalid_text_does_not_raise(spin_box: DecimalSpinBox, text: str):
    spin_box.setKeyboardTracking(True)
    spin_box.lineEdit().setText(text)
    assert spin_box.value() == Decimal("10.00")


def test_trailing_dot_is_a_complete_number(spin_box: DecimalSpinBox):
    spin_box.setKeyboardTracking(True)
    spin_box.lineEdit().setText("1.")
    assert spin_box.value() == Decimal("1.00")


def test_keyboard_tracking_updates_value_without_rewriting_text(spin_box: DecimalSpinBox):
    spin_box.setKeyboardTracking(True)
    spin_box.lineEdit().setText("42.5")
    assert spin_box.value() == Decimal("42.50")
    assert spin_box.lineEdit().text() == "42.5"


def test_return_normalizes_text(qtbot, spin_box: DecimalSpinBox):
    _type(qtbot, spin_box, "42.5")
    qtbot.keyClick(spin_box, Qt.Key.Key_Return)
    assert spin_box.lineEdit().text() == "42.50"


def test_return_clamps_out_of_range_text(qtbot, spin_box: DecimalSpinBox):
    _type(qtbot, spin_box, "150")
    qtbot.keyClick(spin_box, Qt.Key.Key_Return)
    assert spin_box.value() == Decimal("100.00")
    assert spin_box.lineEdit().text() == "100.00"


def test_focus_loss_clamps_out_of_range_text(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    spin_box = DecimalSpinBox()
    spin_box.setRange(0, 100)
    other = QLineEdit()
    layout.addWidget(spin_box)
    layout.addWidget(other)
    host.show()
    host.activateWindow()
    spin_box.setFocus()
    qtbot.waitUntil(spin_box.hasFocus)

    _type(qtbot, spin_box, "150")
    other.setFocus()
    qtbot.waitUntil(other.hasFocus)
    assert spin_box.lineEdit().text() == "100.00"


def test_return_restores_text_that_is_not_a_number(qtbot, spin_box: DecimalSpinBox):
    _type(qtbot, spin_box, "-")
    qtbot.keyClick(spin_box, Qt.Key.Key_Return)
    assert spin_box.value() == Decimal("10.00")
    assert spin_box.lineEdit().text() == "10.00"


def test_validate_states(spin_box: DecimalSpinBox):
    assert spin_box.validate("50", 2)[0] == QValidator.State.Acceptable
    assert spin_box.validate("1.", 2)[0] == QValidator.State.Acceptable
    assert spin_box.validate("-", 1)[0] == QValidator.State.Intermediate
    assert spin_box.validate(".", 1)[0] == QValidator.State.Intermediate
    assert spin_box.validate("500", 3)[0] == QValidator.State.Intermediate  # numeric but out of range
    assert spin_box.validate("abc", 3)[0] == QValidator.State.Invalid


def test_set_range_reclamps_value_and_emits_once(qtbot, spin_box: DecimalSpinBox):
    with qtbot.waitSignal(spin_box.valueChanged) as blocker:
        spin_box.setRange(0, 5)
    assert blocker.args == [Decimal("5.00")]
    assert spin_box.value() == Decimal("5.00")


def test_set_range_swaps_inverted_bounds(spin_box: DecimalSpinBox):
    spin_box.setRange(50, 20)
    assert spin_box.range() == (Decimal("20"), Decimal("50"))


def test_set_decimals_requantizes_and_reformats(spin_box: DecimalSpinBox):
    spin_box.setValue("1.2345")
    assert spin_box.value() == Decimal("1.23")
    spin_box.setDecimals(3)
    assert spin_box.lineEdit().text() == "1.230"
    spin_box.setDecimals(0)
    assert spin_box.value() == Decimal("1")
    assert spin_box.lineEdit().text() == "1"


def test_prefix_and_suffix_round_trip(qtbot, spin_box: DecimalSpinBox):
    spin_box.setPrefix("$")
    spin_box.setSuffix(" USD")
    assert spin_box.lineEdit().text() == "$10.00 USD"
    _type(qtbot, spin_box, "$25 USD")
    qtbot.keyClick(spin_box, Qt.Key.Key_Return)
    assert spin_box.value() == Decimal("25.00")
    assert spin_box.lineEdit().text() == "$25.00 USD"


def test_step_by_and_step_enabled(spin_box: DecimalSpinBox):
    spin_box.setSingleStep("0.5")
    spin_box.stepBy(2)
    assert spin_box.value() == Decimal("11.00")
    spin_box.setValue(100)
    assert spin_box.stepEnabled() == QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
    spin_box.setValue(0)
    assert spin_box.stepEnabled() == QAbstractSpinBox.StepEnabledFlag.StepUpEnabled


def test_correct_to_previous_value_keeps_old_value_when_out_of_range(qtbot, spin_box: DecimalSpinBox):
    spin_box.setKeyboardTracking(False)
    spin_box.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToPreviousValue)
    _type(qtbot, spin_box, "500")
    qtbot.keyClick(spin_box, Qt.Key.Key_Return)
    assert spin_box.value() == Decimal("10.00")
    assert spin_box.lineEdit().text() == "10.00"


def test_designer_properties_do_not_shadow_accessors(spin_box: DecimalSpinBox):
    spin_box.setProperty("decimalPlaces", 1)
    spin_box.setProperty("minimumValue", 2.5)
    spin_box.setProperty("maximumValue", 7.5)
    spin_box.setProperty("stepSize", 0.5)
    assert spin_box.decimals() == 1
    assert spin_box.minimum() == Decimal("2.5")
    assert spin_box.maximum() == Decimal("7.5")
    assert spin_box.singleStep() == Decimal("0.5")
    assert spin_box.property("decimalPlaces") == 1


def test_size_hint_fits_the_widest_bound(qtbot):
    """A direct QAbstractSpinBox subclass gets a hint for the arrow buttons only unless it measures its own text."""
    spin_box = DecimalSpinBox()
    reference = QDoubleSpinBox()
    for widget in (spin_box, reference):
        qtbot.addWidget(widget)
        widget.setRange(-1_000_000, 1_000_000)
        widget.setDecimals(4)
        widget.setSuffix(" mm")

    text_width = spin_box.fontMetrics().horizontalAdvance("-1000000.0000 mm")
    assert spin_box.sizeHint().width() > text_width
    assert spin_box.minimumSizeHint().width() > text_width
    assert abs(spin_box.sizeHint().width() - reference.sizeHint().width()) <= 4


def test_size_hint_follows_range(qtbot):
    spin_box = DecimalSpinBox()
    qtbot.addWidget(spin_box)
    spin_box.setRange(0, 9)
    narrow = spin_box.sizeHint().width()
    spin_box.setRange(0, 999_999_999)
    assert spin_box.sizeHint().width() > narrow


@pytest.mark.parametrize("step", [0, -1, "-0.5"])
def test_single_step_must_be_positive(spin_box: DecimalSpinBox, step):
    with pytest.raises(ValueError):
        spin_box.setSingleStep(step)
    assert spin_box.singleStep() == Decimal("1.00")


def test_user_property_carries_the_decimal_value(qtbot, spin_box: DecimalSpinBox):
    """Item delegates and QDataWidgetMapper read and write an editor through its USER property."""
    user_property = spin_box.metaObject().userProperty()
    assert user_property.name() == "decimalValue"
    assert user_property.read(spin_box) == Decimal("10.00")
    with qtbot.waitSignal(spin_box.valueChanged):
        assert user_property.write(spin_box, Decimal("12.5"))
    assert spin_box.value() == Decimal("12.50")
    assert spin_box.value() == spin_box.decimalValue  # accessor methods stay callable
