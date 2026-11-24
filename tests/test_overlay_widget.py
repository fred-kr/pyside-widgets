import pytest
from PySide6.QtCore import QAbstractAnimation, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pyside_widgets.overlay_widget import IndeterminateSpinner, OverlayWidget

Running = QAbstractAnimation.State.Running
Stopped = QAbstractAnimation.State.Stopped


@pytest.fixture
def parent_widget(qtbot) -> QWidget:
    widget = QWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def overlay(parent_widget: QWidget) -> OverlayWidget:
    return OverlayWidget(parent_widget)


@pytest.fixture
def spinner(overlay: OverlayWidget) -> IndeterminateSpinner:
    return overlay._spinner


def test_spinner_runs_only_while_visible(qtbot, overlay, parent_widget, spinner: IndeterminateSpinner):
    parent_widget.show()
    assert spinner.ani_group.state() == Stopped  # the overlay is hidden

    overlay.show_overlay()
    assert spinner.ani_group.state() == Running

    overlay.hide_overlay()
    assert spinner.ani_group.state() == Stopped
    assert spinner.get_start_angle() == 0
    assert spinner.get_span_angle() == 0


def test_spinner_start_stop(qtbot):
    spinner = IndeterminateSpinner(start=False)
    qtbot.addWidget(spinner)
    spinner.show()
    assert spinner.ani_group.state() == Stopped

    spinner.start()
    assert spinner.ani_group.state() == Running

    spinner.stop()
    assert spinner.ani_group.state() == Stopped

    spinner.hide()
    spinner.start()  # remembered, takes effect when shown
    assert spinner.ani_group.state() == Stopped
    spinner.show()
    assert spinner.ani_group.state() == Running


def test_spinner_is_a_plain_widget(spinner: IndeterminateSpinner):
    assert not hasattr(spinner, "setRange")  # was a QProgressBar although it shows no progress
    spinner.grab()  # forces a paintEvent


def test_spinner_properties(spinner: IndeterminateSpinner):
    spinner.setProperty("startAngle", 90)
    assert spinner.get_start_angle() == 90
    spinner.setProperty("spanAngle", 180)
    assert spinner.get_span_angle() == 180
    spinner.setProperty("strokeWidth", 10)
    assert spinner.get_stroke_width() == 10
    assert spinner.property("strokeWidth") == 10


def test_spinner_color_methods(spinner: IndeterminateSpinner):
    spinner.set_bg_color("red")
    assert spinner._bg_color == QColor("red")
    spinner.set_bar_color("#00FF00")
    assert spinner._bar_color == QColor("#00FF00")


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
    assert overlay.get_text() == "Loading..."

    overlay.hide_overlay()
    assert not overlay.isVisible()
    assert parent_widget.isEnabled()


@pytest.mark.parametrize("how", ["show", "setVisible", "show_overlay", "toggle_overlay"])
def test_every_way_of_showing_covers_and_disables_the_parent(overlay, parent_widget, how):
    parent_widget.resize(400, 300)
    {
        "show": overlay.show,
        "setVisible": lambda: overlay.setVisible(True),
        "show_overlay": overlay.show_overlay,
        "toggle_overlay": lambda: overlay.toggle_overlay(True),
    }[how]()
    assert overlay.size() == parent_widget.size()
    assert not parent_widget.isEnabled()

    overlay.hide()
    assert parent_widget.isEnabled()


def test_hiding_restores_a_parent_that_was_already_disabled(overlay, parent_widget):
    parent_widget.setEnabled(False)
    overlay.show_overlay()
    overlay.hide_overlay()
    assert not parent_widget.isEnabled()


def test_showing_twice_does_not_lose_the_enabled_state(overlay, parent_widget):
    overlay.show_overlay()
    overlay.show_overlay("still working")
    overlay.hide_overlay()
    assert parent_widget.isEnabled()


def test_overlay_toggle(overlay, parent_widget):
    overlay.toggle_overlay(True)
    assert not parent_widget.isEnabled()
    overlay.toggle_overlay(False)
    assert parent_widget.isEnabled()


def test_overlay_set_text(overlay):
    overlay.set_text("Processing")
    assert overlay.get_text() == "Processing"
    assert overlay.property("text") == "Processing"


def test_overlay_set_bar_color(overlay):
    overlay.set_bar_color("blue")
    assert overlay._spinner._bar_color == QColor("blue")
    assert overlay.get_bar_color() == QColor("blue")
    assert overlay.property("barColor") == QColor("blue")


def test_overlay_background_is_painted_without_a_style_sheet(overlay, parent_widget):
    parent_widget.resize(200, 200)
    overlay.set_bg_color(QColor(255, 0, 0, 255))
    assert overlay.get_bg_color() == QColor(255, 0, 0, 255)
    assert overlay.property("bgColor") == QColor(255, 0, 0, 255)
    overlay.show_overlay("Busy")
    assert overlay.styleSheet() == ""
    assert overlay.grab().toImage().pixelColor(2, 2) == QColor(255, 0, 0)


def test_overlay_leaves_sibling_fonts_alone(overlay, parent_widget):
    """No style sheet, so nothing cascades into other children of the covered widget."""
    layout = QVBoxLayout(parent_widget)
    label = QLabel("content")
    layout.addWidget(label)
    family_before = label.font().family()
    overlay.show_overlay("Busy")
    assert label.font().family() == family_before


def test_overlay_follows_parent_resize(qtbot, overlay, parent_widget):
    parent_widget.show()
    overlay.show_overlay()
    parent_widget.resize(640, 480)
    qtbot.waitUntil(lambda: overlay.size() == QSize(640, 480))
    spinner = overlay._spinner
    assert spinner.geometry().center().x() == pytest.approx(320, abs=1)
    assert spinner.geometry().center().y() == pytest.approx(240, abs=1)


def test_overlay_with_no_text(overlay):
    overlay.show_overlay()
    assert overlay.get_text() == ""
    overlay.grab()  # paints without text
