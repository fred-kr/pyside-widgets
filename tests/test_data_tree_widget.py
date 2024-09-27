import pytest
from PySide6 import QtCore, QtWidgets

from pyside_widgets.data_tree_widget import DataTreeWidget, DataTreeWidgetContainer


@pytest.fixture
def sample_data():
    return {"key1": "value1", "key2": 42, "key3": {"nested1": [1, 2, 3], "nested2": {"a": 1, "b": 2}}}


@pytest.fixture
def tree_widget(qtbot):
    widget = DataTreeWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def tree_widget_container(qtbot):
    widget = DataTreeWidgetContainer()
    qtbot.addWidget(widget)
    return widget


def test_data_tree_widget_initialization(tree_widget):
    assert tree_widget.columnCount() == 3
    assert tree_widget.headerItem().text(0) == "Name"
    assert tree_widget.headerItem().text(1) == "Type"
    assert tree_widget.headerItem().text(2) == "Value"


def test_data_tree_widget_set_data(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=True)
    root = tree_widget.invisibleRootItem()
    assert root.childCount() == 3
    assert root.child(0).text(0) == "key1"
    assert root.child(1).text(0) == "key2"
    assert root.child(2).text(0) == "key3"


def test_data_tree_widget_nested_data(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=True)
    root = tree_widget.invisibleRootItem()
    nested_item = root.child(2)  # "key3"
    assert nested_item.childCount() == 2
    assert nested_item.child(0).text(0) == "nested1"
    assert nested_item.child(0).text(1) == "list"


def test_data_tree_widget_filter(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=True)
    root = tree_widget.invisibleRootItem()
    tree_widget.filter_tree("key1")
    assert not root.child(0).isHidden()
    assert root.child(1).isHidden()
    assert root.child(2).isHidden()


def test_data_tree_widget_container_initialization(tree_widget_container):
    assert isinstance(tree_widget_container.search_bar, QtWidgets.QLineEdit)
    assert isinstance(tree_widget_container.btn_sort, QtWidgets.QPushButton)
    assert isinstance(tree_widget_container.data_tree, DataTreeWidget)


def test_data_tree_widget_container_set_data(tree_widget_container, sample_data):
    tree_widget_container.set_data(sample_data, hide_root=True)
    root = tree_widget_container.data_tree.invisibleRootItem()
    assert root.childCount() == 3


def test_data_tree_widget_container_filter(qtbot, tree_widget_container, sample_data):
    tree_widget_container.set_data(sample_data, hide_root=True)
    qtbot.keyClicks(tree_widget_container.search_bar, "key1")

    root = tree_widget_container.data_tree.invisibleRootItem()
    assert not root.child(0).isHidden()
    assert root.child(1).isHidden()
    assert root.child(2).isHidden()


def test_data_tree_widget_container_sort(qtbot, tree_widget_container, sample_data):
    tree_widget_container.set_data(sample_data, hide_root=True)
    qtbot.mouseClick(tree_widget_container.btn_sort, QtCore.Qt.MouseButton.LeftButton)

    root = tree_widget_container.data_tree.invisibleRootItem()
    assert root.child(0).text(0) == "key1"
    assert root.child(1).text(0) == "key2"
    assert root.child(2).text(0) == "key3"
