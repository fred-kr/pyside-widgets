import pytest
from PySide6.QtGui import QColor, QPalette

from pyside_widgets import ColorPickerButton


@pytest.fixture
def button(qtbot) -> ColorPickerButton:
    widget = ColorPickerButton(color=QColor("#336699"))
    qtbot.addWidget(widget)
    return widget


def test_initial_state(button: ColorPickerButton):
    assert button.get_color() == QColor("#336699")
    assert button.text().strip() == "#336699"
    assert not button.icon().isNull()


@pytest.mark.parametrize("color", [None, QColor(), QColor("not a color")])
def test_missing_or_invalid_initial_color_falls_back_to_accent(qtbot, color):
    widget = ColorPickerButton(color=color)
    qtbot.addWidget(widget)
    assert widget.get_color().isValid()
    assert widget.get_color() == widget.palette().color(QPalette.ColorRole.Accent)
    assert not widget.icon().isNull()
    assert widget.text().strip() == widget.get_color().name()


def test_set_color_emits_once_per_change(qtbot, button: ColorPickerButton):
    emitted: list[QColor] = []
    button.sig_color_changed.connect(emitted.append)
    button.set_color(QColor("red"))
    button.set_color(QColor("red"))
    button.set_color("#00ff00")  # anything QColor accepts
    assert emitted == [QColor("red"), QColor("#00ff00")]


def test_invalid_color_is_ignored(button: ColorPickerButton):
    button.set_color(QColor("not a color"))
    assert button.get_color() == QColor("#336699")


def test_alpha_channel_changes_the_text(button: ColorPickerButton):
    button.set_show_alpha_channel(True)
    assert button.text().strip() == "#ff336699"
    assert button.property("showAlphaChannel") is True


def test_show_text_property(button: ColorPickerButton):
    button.setProperty("showText", False)
    assert button.text() == ""
    assert button.get_show_text() is False


def test_background_mode_paints_the_color_without_a_style_sheet(button: ColorPickerButton):
    button.resize(120, 40)
    button.set_show_as_icon(False)
    assert button.icon().isNull()
    assert button.styleSheet() == ""
    center = button.grab().toImage().pixelColor(4, 20)  # left of the centered text
    assert center == QColor("#336699")


def test_swatch_icon_honors_the_device_pixel_ratio(button: ColorPickerButton):
    size = button.iconSize()
    pixmap = button.icon().pixmap(size, button.devicePixelRatioF())
    assert pixmap.devicePixelRatio() == button.devicePixelRatioF()
    assert pixmap.deviceIndependentSize().toSize() == size


def test_user_property_carries_the_color(qtbot, button: ColorPickerButton):
    """Item delegates and QDataWidgetMapper read and write an editor through its USER property."""
    user_property = button.metaObject().userProperty()
    assert user_property.name() == "color"
    assert user_property.read(button) == QColor("#336699")
    with qtbot.waitSignal(button.sig_color_changed):
        assert user_property.write(button, QColor("blue"))
    assert button.color == QColor("blue")
