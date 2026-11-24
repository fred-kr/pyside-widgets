import enum

import pytest
from PySide6.QtCore import Qt

from pyside_widgets.enum_combo_box import NO_SELECTION_TEXT, EnumComboBox


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Shape(enum.Enum):
    CIRCLE = 1


@pytest.fixture
def combo(qtbot) -> EnumComboBox[Color]:
    widget: EnumComboBox[Color] = EnumComboBox(enum_class=Color)
    qtbot.addWidget(widget)
    return widget


def _record(combo: EnumComboBox) -> list[object]:
    emitted: list[object] = []
    combo.sig_current_enum_changed.connect(emitted.append)
    return emitted


def test_populated_from_enum(combo: EnumComboBox[Color]):
    assert combo.count() == 3
    assert [combo.itemText(i) for i in range(3)] == ["RED", "GREEN", "BLUE"]
    assert combo.get_current_enum() is Color.RED


def test_set_and_get_current_enum(qtbot, combo: EnumComboBox[Color]):
    with qtbot.waitSignal(combo.sig_current_enum_changed) as blocker:
        combo.set_current_enum(Color.BLUE)
    assert blocker.args == [Color.BLUE]
    assert combo.get_current_enum() is Color.BLUE


def test_setting_the_current_member_again_emits_nothing(combo: EnumComboBox[Color]):
    combo.set_current_enum(Color.GREEN)
    emitted = _record(combo)
    combo.set_current_enum(Color.GREEN)
    assert emitted == []


def test_custom_text_and_tooltip(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    widget.set_enum_class(Color, text_data=lambda m: m.name.lower(), doc_data=lambda m: f"doc {m.value}")
    assert widget.itemText(1) == "green"
    assert widget.itemData(1, role=Qt.ItemDataRole.ToolTipRole) == "doc 2"


def test_allow_none_adds_row_and_keeps_selection(combo: EnumComboBox[Color]):
    combo.set_current_enum(Color.GREEN)
    combo.set_allow_none(True)
    assert combo.count() == 4
    assert combo.itemText(0) == NO_SELECTION_TEXT
    assert combo.get_current_enum() is Color.GREEN

    combo.set_current_enum(None)
    assert combo.currentIndex() == 0
    assert combo.get_current_enum() is None

    combo.set_allow_none(False)
    assert combo.count() == 3


def test_toggling_allow_none_emits_only_real_changes(combo: EnumComboBox[Color]):
    """Rebuilding the rows clears and refills the model; none of that may reach listeners."""
    combo.set_current_enum(Color.GREEN)
    emitted = _record(combo)

    combo.set_allow_none(True)
    assert emitted == []  # GREEN is still selected

    combo.set_current_enum(None)
    assert emitted == [None]

    combo.set_allow_none(False)  # the "no selection" row disappears, the first member takes over
    assert emitted == [None, Color.RED]


def test_changing_the_enum_class_emits_once(combo: EnumComboBox[Color]):
    emitted = _record(combo)
    combo.set_enum_class(Shape)  # pyright: ignore[reportArgumentType]
    assert emitted == [Shape.CIRCLE]
    combo.set_enum_class(None)
    assert emitted == [Shape.CIRCLE, None]


def test_allow_none_keeps_custom_text(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    widget.set_enum_class(Color, text_data=lambda m: m.name.lower())
    widget.set_allow_none(True)
    assert widget.itemText(1) == "red"


def test_set_none_without_allow_none_raises(combo: EnumComboBox[Color]):
    with pytest.raises(ValueError):
        combo.set_current_enum(None)


def test_set_member_of_another_enum_raises(combo: EnumComboBox[Color]):
    with pytest.raises(ValueError, match="is not a member of Color"):
        combo.set_current_enum(Shape.CIRCLE)  # pyright: ignore[reportArgumentType]
    assert combo.get_current_enum() is Color.RED


def test_no_enum_class(qtbot):
    widget: EnumComboBox[Color] = EnumComboBox()
    qtbot.addWidget(widget)
    assert widget.count() == 0
    assert widget.get_current_enum() is None
    with pytest.raises(ValueError):
        widget.set_current_enum(Color.RED)


def test_allow_none_property(combo: EnumComboBox[Color]):
    combo.setProperty("allowNone", True)
    assert combo.property("allowNone") is True
    assert combo.get_allow_none() is True
    assert combo.count() == 4


def test_user_property_carries_the_member(qtbot, combo: EnumComboBox[Color]):
    """Item delegates and QDataWidgetMapper read and write an editor through its USER property."""
    user_property = combo.metaObject().userProperty()
    assert user_property.name() == "currentEnum"
    assert combo.property("currentEnum") is Color.RED
    with qtbot.waitSignal(combo.sig_current_enum_changed) as blocker:
        assert combo.setProperty("currentEnum", Color.BLUE)
    assert blocker.args == [Color.BLUE]
    assert combo.currentEnum is Color.BLUE

    # QMetaProperty.write hands a member over as its plain value; the setter maps it back.
    assert user_property.write(combo, Color.GREEN)
    assert combo.get_current_enum() is Color.GREEN


@pytest.mark.parametrize(("enum_class", "raw", "member"), [(Color, 3, Color.BLUE)])
def test_plain_value_of_a_member_is_accepted(qtbot, enum_class, raw, member):
    widget = EnumComboBox(enum_class=enum_class)
    qtbot.addWidget(widget)
    widget.set_current_enum(raw)
    assert widget.get_current_enum() is member
    with pytest.raises(ValueError):
        widget.set_current_enum(99)


def test_members_stay_available_as_item_data(combo: EnumComboBox[Color]):
    combo.set_current_enum(Color.GREEN)
    assert combo.currentData() == Color.GREEN
    assert combo.findData(Color.BLUE) == 2


def test_deprecated_getter_still_works_and_warns(combo: EnumComboBox[Color]):
    with pytest.warns(DeprecationWarning, match="get_current_enum"):
        assert combo.current_enum() is Color.RED


def test_uic_setter_spelling(combo: EnumComboBox[Color]):
    combo.setAllowNone(True)  # what pyside6-uic generates for the allowNone property
    assert combo.get_allow_none() is True


class Separator(enum.StrEnum):
    Tab = "\t"
    Comma = ","


class Level(enum.IntEnum):
    Low = 1
    High = 2


@pytest.mark.parametrize(("enum_class", "member"), [(Separator, Separator.Comma), (Level, Level.High)])
def test_str_and_int_enum_members_keep_their_type(qtbot, enum_class, member):
    """Qt stores str/int subclasses as plain QString/int item data; the widget must hand back the member."""
    widget = EnumComboBox(enum_class=enum_class)
    qtbot.addWidget(widget)
    with qtbot.waitSignal(widget.sig_current_enum_changed) as blocker:
        widget.set_current_enum(member)
    assert widget.get_current_enum() is member
    assert blocker.args == [member]

    # setProperty degrades a StrEnum member to a plain str on the way in; the widget still selects the member.
    widget.setCurrentIndex(0)
    assert widget.setProperty("currentEnum", member)
    assert widget.get_current_enum() is member
    assert widget.set_current_enum(member.value) is None
    assert widget.get_current_enum() is member
