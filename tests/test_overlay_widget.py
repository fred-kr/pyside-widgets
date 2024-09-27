import sys

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from pyside_widgets.overlay_widget import IndeterminateSpinner, OverlayWidget


@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the test module."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app
    if not QtWidgets.QApplication.instance():
        app.quit()


@pytest.fixture
def parent_widget(app):
    """Provide a parent widget for testing."""
    return QtWidgets.QWidget()


@pytest.fixture
def overlay(parent_widget: QtWidgets.QWidget) -> OverlayWidget:
    """Provide a fresh OverlayWidget for each test."""
    return OverlayWidget(parent_widget)


@pytest.fixture
def spinner(overlay: OverlayWidget) -> IndeterminateSpinner:
    """Provide a fresh IndeterminateSpinner for each test."""
    return overlay._spinner


def test_spinner_start_stop(spinner: IndeterminateSpinner):
    # Stop the spinner
    spinner.stop()
    assert spinner.ani_group.state() == QtCore.QAbstractAnimation.State.Stopped
    assert spinner.startAngle == 0
    assert spinner.spanAngle == 0

    # Start the spinner
    spinner.start()
    assert spinner.ani_group.state() == QtCore.QAbstractAnimation.State.Running


def test_spinner_properties(spinner: IndeterminateSpinner):
    # Test startAngle property
    spinner.startAngle = 90
    assert spinner.startAngle == 90

    # Test spanAngle property
    spinner.spanAngle = 180
    assert spinner.spanAngle == 180

    # Test stroke_width property
    spinner.stroke_width = 10
    assert spinner.stroke_width == 10


def test_spinner_color_methods(spinner: IndeterminateSpinner):
    # Set background color
    spinner.set_bg_color("red")
    assert spinner._bg_color == QtGui.QColor("red")

    # Set bar color
    spinner.set_bar_color("#00FF00")
    assert spinner._bar_color == QtGui.QColor("#00FF00")


def test_spinner_invalid_color(spinner: IndeterminateSpinner):
    # Set invalid background color
    spinner.set_bg_color("invalid_color")
    assert spinner._bg_color.isValid()  # Should remain unchanged

    # Set invalid bar color
    spinner.set_bar_color("invalid_color")
    assert spinner._bar_color.isValid()  # Should remain unchanged


def test_overlay_initial_state(overlay, parent_widget):
    # Overlay should be hidden initially
    assert not overlay.isVisible()
    assert parent_widget.isEnabled()


def test_overlay_show_hide(overlay, parent_widget):
    # Show overlay
    overlay.show_overlay("Loading...")
    assert overlay.isVisibleTo(parent_widget)
    assert not parent_widget.isEnabled()
    assert overlay._text.text() == "Loading..."

    # Hide overlay
    overlay.hide_overlay()
    assert not overlay.isVisible()
    assert parent_widget.isEnabled()


def test_overlay_set_text(overlay):
    overlay.set_text("Processing")
    assert overlay._text.text() == "Processing"


def test_overlay_set_spinner_color(overlay):
    overlay.set_spinner_color("blue")
    assert overlay._spinner._bar_color == QtGui.QColor("blue")


def test_overlay_set_background_color(overlay):
    overlay.set_background_color(255, 0, 0, 200)
    expected_style = "background: rgba(255, 0, 0, 200);"
    assert overlay._container.styleSheet() == expected_style


def test_overlay_geometry(overlay, parent_widget):
    parent_widget.resize(400, 300)
    overlay.show_overlay()
    assert overlay.geometry() == parent_widget.geometry()
    assert overlay._container.size() == parent_widget.size()


def test_overlay_with_no_text(overlay):
    overlay.show_overlay()
    assert overlay._text.text() == ""
