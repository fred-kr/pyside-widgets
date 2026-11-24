import pytest
from PySide6.QtCore import QPoint, QPointF, QRect, Qt
from PySide6.QtGui import QImage, QPainter, QStandardItem, QStandardItemModel, QWheelEvent
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionViewItem

from pyside_widgets.grouped_combo_box import GroupedComboBox, ItemType, ItemTypeRole


def _item(combo_box: GroupedComboBox, row: int) -> QStandardItem:
    model = combo_box.model()
    assert isinstance(model, QStandardItemModel)
    item = model.item(row)
    assert item is not None
    return item


@pytest.fixture
def combo_box(qtbot) -> GroupedComboBox:
    """Provide a fresh GroupedComboBox instance for each test."""
    grouped_combo_box = GroupedComboBox()
    qtbot.addWidget(grouped_combo_box)

    return grouped_combo_box


@pytest.fixture
def filled(combo_box: GroupedComboBox) -> GroupedComboBox:
    """Rows: 0 header, 1-2 children, 3 separator, 4 header, 5 child."""
    combo_box.add_parent_item("Group 1")
    combo_box.add_child_item("Item 1", "d1")
    combo_box.add_child_item("Item 2", "d2")
    combo_box.add_separator()
    combo_box.add_parent_item("Group 2")
    combo_box.add_child_item("Item 3", "d3")
    return combo_box


def test_add_separator(combo_box: GroupedComboBox):
    combo_box.add_separator()
    item = _item(combo_box, 0)
    assert item.data(ItemTypeRole) == ItemType.SEPARATOR
    assert not (item.flags() & Qt.ItemFlag.ItemIsSelectable)


def test_add_parent_item(combo_box: GroupedComboBox):
    combo_box.add_parent_item("Parent")
    item = _item(combo_box, 0)
    assert item.data(ItemTypeRole) == ItemType.PARENT
    assert not (item.flags() & Qt.ItemFlag.ItemIsSelectable)
    assert item.font().bold()


def test_add_child_item(combo_box: GroupedComboBox):
    test_data = {"key": "value"}
    combo_box.add_child_item("Child", test_data)
    item = _item(combo_box, 0)
    assert item.data(ItemTypeRole) == ItemType.CHILD
    assert item.flags() & Qt.ItemFlag.ItemIsSelectable
    assert item.data(Qt.ItemDataRole.UserRole) == test_data


def test_header_never_becomes_current_on_insert(combo_box: GroupedComboBox):
    """QComboBox makes the first inserted row current; for a header that must be undone."""
    combo_box.add_parent_item("Group 1")
    assert combo_box.currentIndex() == -1
    combo_box.add_child_item("Item 1", "d1")
    assert combo_box.currentIndex() == 1
    assert combo_box.currentText() == "Item 1"
    combo_box.add_child_item("Item 2", "d2")
    assert combo_box.currentIndex() == 1  # an existing selection is left alone


def test_keyboard_navigation_skips_headers_and_separators(qtbot, filled: GroupedComboBox):
    filled.show()
    filled.setCurrentIndex(1)
    qtbot.keyClick(filled, Qt.Key.Key_Up)
    assert filled.currentIndex() == 1  # row 0 is a header

    filled.setCurrentIndex(2)
    qtbot.keyClick(filled, Qt.Key.Key_Down)
    assert filled.currentIndex() == 5  # rows 3 and 4 are a separator and a header


def test_wheel_skips_headers_and_separators(filled: GroupedComboBox):
    filled.show()
    filled.setFocus()
    filled.setCurrentIndex(2)
    center = QPointF(filled.rect().center())
    wheel_down = QWheelEvent(
        center,
        filled.mapToGlobal(center),
        QPoint(0, 0),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(filled, wheel_down)
    assert filled.currentIndex() == 5


@pytest.fixture
def instant_popup(qapp):
    """The popup ignores mouse releases for one double-click interval after it opens; make that interval zero."""
    interval = QApplication.doubleClickInterval()
    QApplication.setDoubleClickInterval(0)
    yield
    QApplication.setDoubleClickInterval(interval)


def _hover_and_click(qtbot, combo_box: GroupedComboBox, row: int, hover_first: int | None = None) -> None:
    viewport = combo_box.view().viewport()
    for hovered in (hover_first, row):
        if hovered is not None:
            qtbot.mouseMove(viewport, combo_box.view().visualRect(combo_box.model().index(hovered, 0)).center())
            qtbot.wait(10)
    qtbot.mouseClick(
        viewport, Qt.MouseButton.LeftButton, pos=combo_box.view().visualRect(combo_box.model().index(row, 0)).center()
    )
    qtbot.wait(10)


@pytest.mark.parametrize("row", [4, 3], ids=["header", "separator"])
def test_clicking_a_header_or_separator_in_the_popup_selects_nothing(qtbot, instant_popup, filled, row):
    """The popup selects the last hovered row on any release, so an unguarded click here would pick "Item 2"."""
    filled.show()
    filled.setCurrentIndex(1)
    filled.showPopup()
    qtbot.wait(30)

    _hover_and_click(qtbot, filled, row, hover_first=2)
    assert filled.currentIndex() == 1
    assert filled.view().isVisible()  # the popup stays open

    _hover_and_click(qtbot, filled, 5)
    assert filled.currentIndex() == 5
    assert not filled.view().isVisible()


def test_keyboard_in_the_popup_skips_headers(qtbot, instant_popup, filled):
    filled.show()
    filled.setCurrentIndex(2)
    filled.showPopup()
    qtbot.wait(30)
    qtbot.keyClick(filled.view(), Qt.Key.Key_Down)
    qtbot.keyClick(filled.view(), Qt.Key.Key_Return)
    assert filled.currentIndex() == 5


def test_current_data_is_the_base_class_behavior(filled: GroupedComboBox):
    filled.setCurrentIndex(1)
    assert filled.currentData() == "d1"
    assert filled.currentData(Qt.ItemDataRole.DisplayRole) == "Item 1"

    # A header selected programmatically carries no user data.
    filled.setCurrentIndex(0)
    assert filled.currentData() is None

    # Rows added through the plain QComboBox API keep their data.
    filled.addItem("plain", "plain-data")
    filled.setCurrentIndex(filled.count() - 1)
    assert filled.currentData() == "plain-data"


def test_delegate_sizes_and_paints_every_row_type(filled: GroupedComboBox):
    delegate = filled.itemDelegate()
    option = QStyleOptionViewItem()
    option.state = QStyle.StateFlag.State_Enabled
    option.rect = QRect(0, 0, 100, 20)

    assert delegate.sizeHint(option, filled.model().index(3, 0)).height() == 5

    image = QImage(100, 20, QImage.Format.Format_ARGB32_Premultiplied)
    with QPainter(image) as painter:
        for row in range(filled.count()):
            delegate.paint(painter, option, filled.model().index(row, 0))
    assert option.rect == QRect(0, 0, 100, 20)  # the view reuses its option, so the delegate must not modify it
