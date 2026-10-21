import enum

import pytest
from PySide6.QtCore import Qt

from pyside_widgets.enum_combo_box import NO_SELECTION_TEXT, EnumComboBox


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


@pytest.fixture
def combo(qtbot) -> EnumComboBox[Color]:
    widget: EnumComboBox[Color] = EnumComboBox(enum_class=Color)
    qtbot.addWidget(widget)
    return widget


def test_populated_from_enum(combo: EnumComboBox[Color]):
    assert combo.count() == 3
    assert [combo.itemText(i) for i in range(3)] == ["RED", "GREEN", "BLUE"]
    assert combo.current_enum() is Color.RED


def test_set_and_get_current_enum(qtbot, combo: EnumComboBox[Color]):
    with qtbot.waitSignal(combo.sig_current_enum_changed) as blocker:
        combo.set_current_enum(Color.BLUE)
    assert blocker.args == [Color.BLUE]
    assert combo.current_enum() is Color.BLUE


def test_custom_text_and_tooltip(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    widget.set_enum_class(Color, text_data=lambda m: m.name.lower(), doc_data=lambda m: f"doc {m.value}")
    assert widget.itemText(1) == "green"
    assert widget.itemData(1, role=Qt.ItemDataRole.ToolTipRole) == "doc 2"


def test_allow_none_adds_row_and_keeps_selection(combo: EnumComboBox[Color]):
    combo.set_current_enum(Color.GREEN)
    combo.setAllowNone(True)
    assert combo.count() == 4
    assert combo.itemText(0) == NO_SELECTION_TEXT
    assert combo.current_enum() is Color.GREEN

    combo.set_current_enum(None)
    assert combo.currentIndex() == 0
    assert combo.current_enum() is None

    combo.setAllowNone(False)
    assert combo.count() == 3


def test_allow_none_keeps_custom_text(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    widget.set_enum_class(Color, text_data=lambda m: m.name.lower())
    widget.setAllowNone(True)
    assert widget.itemText(1) == "red"


def test_set_none_without_allow_none_raises(combo: EnumComboBox[Color]):
    with pytest.raises(ValueError):
        combo.set_current_enum(None)


def test_no_enum_class(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    assert widget.count() == 0
    assert widget.current_enum() is None
    with pytest.raises(ValueError):
        widget.set_current_enum(Color.RED)


def test_allow_none_property(combo: EnumComboBox[Color]):
    combo.setProperty("allowNone", True)
    assert combo.property("allowNone") is True
    assert combo.count() == 4
