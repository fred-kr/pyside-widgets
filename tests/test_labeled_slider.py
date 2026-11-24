import pytest
from PySide6.QtWidgets import QSlider

from pyside_widgets import LabeledSlider, ValueSlider


@pytest.fixture
def slider(qtbot) -> LabeledSlider:
    widget = LabeledSlider(title="Gain")
    qtbot.addWidget(widget)
    return widget


def test_range_updates_the_labels(qtbot, slider: LabeledSlider):
    with qtbot.waitSignal(slider.rangeChanged) as blocker:
        slider.setRange(-5, 250)
    assert blocker.args == [-5, 250]
    assert slider.minimum_label.text() == "-5"
    assert slider.maximum_label.text() == "250"
    assert (slider.minimum(), slider.maximum()) == (-5, 250)


def test_value_signal_is_forwarded(qtbot, slider: LabeledSlider):
    with qtbot.waitSignal(slider.valueChanged) as blocker:
        slider.setValue(42)
    assert blocker.args == [42]
    assert slider.value() == 42
    assert slider.slider.value() == 42


def test_title_property(slider: LabeledSlider):
    assert slider.get_title() == "Gain"
    assert slider.title_label.isVisibleTo(slider)
    slider.setProperty("title", "")
    assert not slider.title_label.isVisibleTo(slider)
    slider.set_title("Offset")
    assert slider.property("title") == "Offset"
    assert slider.title_label.isVisibleTo(slider)


def test_user_property_carries_the_value(qtbot, slider: LabeledSlider):
    user_property = slider.metaObject().userProperty()
    assert user_property.name() == "sliderValue"
    with qtbot.waitSignal(slider.valueChanged):
        assert user_property.write(slider, 7)
    assert slider.value() == 7  # the accessor that mirrors QSlider stays a method


@pytest.mark.parametrize("position", list(LabeledSlider.TitleLabelPosition))
def test_every_title_position_builds_and_paints(qtbot, position):
    widget = LabeledSlider(title="Title", title_pos=position)
    qtbot.addWidget(widget)
    widget.grab()


def test_value_slider_reserves_room_for_the_value_text(qtbot):
    """The extra height follows the font instead of a fixed pixel count."""
    plain = QSlider()
    value_slider = ValueSlider()
    for widget in (plain, value_slider):
        qtbot.addWidget(widget)
        widget.setOrientation(plain.orientation().Horizontal)

    line_height = value_slider.fontMetrics().height()
    assert value_slider.sizeHint().height() == plain.sizeHint().height() + 2 * line_height
    assert value_slider.minimumSizeHint().height() == value_slider.sizeHint().height()

    font = value_slider.font()
    font.setPointSize(font.pointSize() * 2)
    value_slider.setFont(font)
    assert value_slider.sizeHint().height() > plain.sizeHint().height() + 2 * line_height


def test_orientation_stub_is_gone(slider: LabeledSlider):
    assert not hasattr(slider, "setOrientation")
