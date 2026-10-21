from decimal import Decimal

import pytest
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox

from pyside_widgets.decimal_spin_box import DecimalSpinBox


@pytest.fixture
def spin_box(qtbot) -> DecimalSpinBox:
    widget = DecimalSpinBox()
    qtbot.addWidget(widget)
    widget.setRange(0, 100)
    widget.setDecimals(2)
    widget.setValue(10)
    return widget


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


def test_editing_finished_normalizes_text(spin_box: DecimalSpinBox):
    spin_box.lineEdit().setText("42.5")
    spin_box.lineEdit().editingFinished.emit()
    assert spin_box.lineEdit().text() == "42.50"


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


def test_prefix_and_suffix_round_trip(spin_box: DecimalSpinBox):
    spin_box.setPrefix("$")
    spin_box.setSuffix(" USD")
    assert spin_box.lineEdit().text() == "$10.00 USD"
    spin_box.lineEdit().setText("$25 USD")
    spin_box.lineEdit().editingFinished.emit()
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


def test_correct_to_previous_value_keeps_old_value_when_out_of_range(spin_box: DecimalSpinBox):
    spin_box.setKeyboardTracking(False)
    spin_box.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToPreviousValue)
    spin_box.lineEdit().setText("500")
    spin_box.lineEdit().editingFinished.emit()
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
