import sys

import pytest
from PySide6 import QtCore, QtWidgets

from pyside_widgets.grouped_combo_box import GroupedComboBox, ItemType, ItemTypeRole


@pytest.fixture(scope="module")
def app():
    """Create a QApplication instance for the test suite."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app
    if not QtWidgets.QApplication.instance():
        app.quit()


@pytest.fixture
def combo_box(app):
    """Provide a fresh GroupedComboBox instance for each test."""
    return GroupedComboBox()


def test_add_separator(combo_box: GroupedComboBox):
    combo_box.add_separator()
    model = combo_box.model()
    item = model.item(0)
    assert item.data(ItemTypeRole) == ItemType.SEPARATOR
    assert not (item.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable)


def test_add_parent_item(combo_box: GroupedComboBox):
    combo_box.add_parent_item("Parent")
    model = combo_box.model()
    item = model.item(0)
    assert item.data(ItemTypeRole) == ItemType.PARENT
    assert not (item.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable)
    assert item.font().bold()


def test_add_child_item(combo_box: GroupedComboBox):
    test_data = {"key": "value"}
    combo_box.add_child_item("Child", test_data)
    model = combo_box.model()
    item = model.item(0)
    assert item.data(ItemTypeRole) == ItemType.CHILD
    assert item.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable
    assert item.data(QtCore.Qt.ItemDataRole.UserRole) == test_data


def test_selection_behavior(combo_box: GroupedComboBox):
    # Add items
    combo_box.add_parent_item("Parent")
    combo_box.add_child_item("Child", "child_data")
    combo_box.add_separator()
    combo_box.add_child_item("Child 2", "child_data_2")

    # Attempt to select parent item (should not be selectable)
    combo_box.setCurrentIndex(0)
    assert combo_box.currentData() is None

    # Select first child item
    combo_box.setCurrentIndex(1)
    assert combo_box.currentData() == "child_data"

    # Attempt to select separator (should not be selectable)
    combo_box.setCurrentIndex(2)
    assert combo_box.currentData() is None

    # Select second child item
    combo_box.setCurrentIndex(3)
    assert combo_box.currentData() == "child_data_2"


def test_current_data(combo_box: GroupedComboBox):
    # Add items
    combo_box.add_parent_item("Parent")
    combo_box.add_child_item("Child", 123)

    # Select child item
    combo_box.setCurrentIndex(1)
    assert combo_box.currentData() == 123

    # Select parent item (should return None)
    combo_box.setCurrentIndex(0)
    assert combo_box.currentData() is None


def test_visual_properties(combo_box: GroupedComboBox):
    # Add items
    combo_box.add_parent_item("Parent")
    combo_box.add_child_item("Child", None)

    # Fetch the delegate and option
    delegate = combo_box.itemDelegate()
    option = QtWidgets.QStyleOptionViewItem()
    option.state = QtWidgets.QStyle.StateFlag.State_Enabled
    option.rect = QtCore.QRect(0, 0, 100, 20)

    # Check size hint for separator
    combo_box.add_separator()
    separator_index = combo_box.model().index(2, 0)
    size_hint = delegate.sizeHint(option, separator_index)
    assert size_hint.height() == 5
