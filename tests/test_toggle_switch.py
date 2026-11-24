import pytest
from PySide6.QtGui import QImage

from pyside_widgets.toggle_switch import AnimatedToggleSwitch, ToggleSwitch


def test_plain_switch_has_pulse_radius(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    assert switch.get_pulse_radius() == 0
    assert switch.get_handle_position() == 0
    assert switch.property("pulseRadius") == 0
    assert switch.property("handlePosition") == 0


def test_plain_switch_moves_handle_on_toggle(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    switch.setChecked(True)
    assert switch.get_handle_position() == 1.0
    switch.setChecked(False)
    assert switch.get_handle_position() == 0.0


def test_animated_switch_reaches_end_position(qtbot):
    switch = AnimatedToggleSwitch()
    qtbot.addWidget(switch)
    switch.show()
    switch.setChecked(True)
    qtbot.waitUntil(lambda: switch.get_handle_position() == pytest.approx(1.0), timeout=2000)
    switch.setChecked(False)
    qtbot.waitUntil(lambda: switch.get_handle_position() == pytest.approx(0.0), timeout=2000)


def test_paint_does_not_raise(qtbot):
    for cls in (ToggleSwitch, AnimatedToggleSwitch):
        switch = cls()
        qtbot.addWidget(switch)
        switch.show()
        switch.setChecked(True)
        switch.setFocus()
        switch.grab()  # forces a paintEvent


def test_disabled_switch_is_drawn_differently(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    switch.setChecked(True)
    enabled = switch.grab().toImage().convertToFormat(QImage.Format.Format_ARGB32)
    switch.setEnabled(False)
    disabled = switch.grab().toImage().convertToFormat(QImage.Format.Format_ARGB32)
    assert enabled != disabled


def test_user_property_is_the_checked_state(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    assert switch.metaObject().userProperty().name() == "checked"
