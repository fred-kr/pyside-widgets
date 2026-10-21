import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from pyside_widgets.overlay_widget import IndeterminateSpinner, OverlayWidget


@pytest.fixture
def parent_widget(qtbot) -> QtWidgets.QWidget:
    widget = QtWidgets.QWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def overlay(parent_widget: QtWidgets.QWidget) -> OverlayWidget:
    return OverlayWidget(parent_widget)


@pytest.fixture
def spinner(overlay: OverlayWidget) -> IndeterminateSpinner:
    return overlay._spinner


def test_spinner_start_stop(spinner: IndeterminateSpinner):
    spinner.stop()
    assert spinner.ani_group.state() == QtCore.QAbstractAnimation.State.Stopped
    assert spinner.get_start_angle() == 0
    assert spinner.get_span_angle() == 0

    spinner.start()
    assert spinner.ani_group.state() == QtCore.QAbstractAnimation.State.Running


def test_spinner_properties(spinner: IndeterminateSpinner):
    spinner.setProperty("startAngle", 90)
    assert spinner.get_start_angle() == 90
    spinner.setProperty("spanAngle", 180)
    assert spinner.get_span_angle() == 180
    spinner.setProperty("stroke_width", 10)
    assert spinner.get_stroke_width() == 10
    assert spinner.property("stroke_width") == 10


def test_spinner_color_methods(spinner: IndeterminateSpinner):
    spinner.set_bg_color("red")
    assert spinner._bg_color == QtGui.QColor("red")
    spinner.set_bar_color("#00FF00")
    assert spinner._bar_color == QtGui.QColor("#00FF00")


def test_spinner_invalid_color_is_ignored(spinner: IndeterminateSpinner):
    spinner.set_bg_color("invalid_color")
    assert spinner._bg_color.isValid()
    spinner.set_bar_color("invalid_color")
    assert spinner._bar_color.isValid()


def test_overlay_initial_state(overlay, parent_widget):
    assert not overlay.isVisible()
    assert parent_widget.isEnabled()


def test_overlay_show_hide(overlay, parent_widget):
    overlay.show_overlay("Loading...")
    assert overlay.isVisibleTo(parent_widget)
    assert not parent_widget.isEnabled()
    assert overlay._text.text() == "Loading..."

    overlay.hide_overlay()
    assert not overlay.isVisible()
    assert parent_widget.isEnabled()


def test_overlay_toggle(overlay, parent_widget):
    overlay.toggle_overlay(True)
    assert not parent_widget.isEnabled()
    overlay.toggle_overlay(False)
    assert parent_widget.isEnabled()


def test_overlay_set_text(overlay):
    overlay.set_text("Processing")
    assert overlay._text.text() == "Processing"
    assert overlay.property("text") == "Processing"


def test_overlay_set_bar_color(overlay):
    overlay.set_bar_color("blue")
    assert overlay._spinner._bar_color == QtGui.QColor("blue")
    assert overlay.get_bar_color() == QtGui.QColor("blue")


def test_overlay_set_bg_color(overlay):
    overlay.set_bg_color(QtGui.QColor(255, 0, 0, 200))
    assert overlay._container.styleSheet() == "background: rgba(255, 0, 0, 200);"
    assert overlay.get_bg_color() == QtGui.QColor(255, 0, 0, 200)


def test_overlay_geometry(overlay, parent_widget):
    parent_widget.resize(400, 300)
    overlay.show_overlay()
    assert overlay.size() == parent_widget.size()
    assert overlay._container.size() == parent_widget.size()


def test_overlay_follows_parent_resize(qtbot, overlay, parent_widget):
    parent_widget.show()
    overlay.show_overlay()
    parent_widget.resize(640, 480)
    qtbot.waitUntil(lambda: overlay.size() == QtCore.QSize(640, 480))
    assert overlay._container.size() == QtCore.QSize(640, 480)


def test_overlay_with_no_text(overlay):
    overlay.show_overlay()
    assert overlay._text.text() == ""
