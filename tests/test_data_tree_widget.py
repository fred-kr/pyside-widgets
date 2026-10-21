import pytest
from PySide6 import QtCore, QtWidgets

from pyside_widgets.data_tree_widget import DataTreeWidget, SearchableDataTreeWidget


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
    widget = SearchableDataTreeWidget()
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
    assert root.child(0).text(1) == "str"
    assert root.child(0).text(2) == "value1"


def test_data_tree_widget_visible_root(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=False)
    root = tree_widget.invisibleRootItem()
    assert root.childCount() == 1
    assert root.child(0).text(1) == "dict"
    assert root.child(0).childCount() == 3


def test_data_tree_widget_nested_data(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=True)
    root = tree_widget.invisibleRootItem()
    nested_item = root.child(2)  # "key3"
    assert nested_item.childCount() == 2
    assert nested_item.child(0).text(0) == "nested1"
    assert nested_item.child(0).text(1) == "list"
    assert nested_item.child(0).childCount() == 3
    assert nested_item.child(0).child(2).text(2) == "3"


def test_data_tree_widget_filter(tree_widget, sample_data):
    tree_widget.set_data(sample_data, hide_root=True)
    root = tree_widget.invisibleRootItem()
    tree_widget.filter_tree("KEY1")
    assert not root.child(0).isHidden()
    assert root.child(1).isHidden()
    assert root.child(2).isHidden()


def test_filter_before_set_data_and_after_clear(tree_widget, sample_data):
    tree_widget.filter_tree("x")  # must not raise
    tree_widget.set_data(sample_data)
    tree_widget.clear()
    assert tree_widget.topLevelItemCount() == 0
    tree_widget.filter_tree("x")


def test_long_description_gets_full_text_editor(tree_widget):
    long_text = "x" * 250
    tree_widget.set_data({"long": long_text})
    item = tree_widget.invisibleRootItem().child(0)
    assert item.text(2).endswith("...")
    assert len(item.text(2)) == 100
    editor = tree_widget.itemWidget(item.child(0), 0)
    assert isinstance(editor, QtWidgets.QPlainTextEdit)
    assert editor.toPlainText() == long_text


def test_toggle_sort_alternates(tree_widget):
    tree_widget.set_data({"b": 1, "a": 2, "c": 3})
    root = tree_widget.invisibleRootItem()
    tree_widget.toggle_sort()
    assert [root.child(i).text(0) for i in range(3)] == ["a", "b", "c"]
    tree_widget.toggle_sort()
    assert [root.child(i).text(0) for i in range(3)] == ["c", "b", "a"]


def test_array_small_renders_table(tree_widget):
    numpy = pytest.importorskip("numpy")
    tree_widget.set_data({"arr": numpy.arange(12).reshape(3, 4)})
    item = tree_widget.invisibleRootItem().child(0)
    assert item.text(1) == "ndarray"
    assert item.text(2) == "shape=(3, 4) dtype=int64"
    table = tree_widget.itemWidget(item.child(0), 0)
    assert isinstance(table, QtWidgets.QTableWidget)
    assert (table.rowCount(), table.columnCount()) == (3, 4)
    cell = table.item(2, 3)
    assert cell is not None and cell.text() == "11"


def test_array_large_renders_summary_button(tree_widget):
    numpy = pytest.importorskip("numpy")
    tree_widget.set_data({"arr": numpy.arange(5000, dtype=float)})
    item = tree_widget.invisibleRootItem().child(0)
    button = tree_widget.itemWidget(item.child(0), 0)
    assert isinstance(button, QtWidgets.QPushButton)
    assert button.text().startswith("Array summary: min=0.0, max=4999.0, mean=2499.50")


def test_array_1d_and_0d(tree_widget):
    numpy = pytest.importorskip("numpy")
    tree_widget.set_data({"vec": numpy.array([1, 2, 3]), "scalar": numpy.array(7)})
    root = tree_widget.invisibleRootItem()
    vec_table = tree_widget.itemWidget(root.child(0).child(0), 0)
    assert (vec_table.rowCount(), vec_table.columnCount()) == (3, 1)
    scalar_table = tree_widget.itemWidget(root.child(1).child(0), 0)
    assert (scalar_table.rowCount(), scalar_table.columnCount()) == (1, 1)
    cell = scalar_table.item(0, 0)
    assert cell is not None and cell.text() == "7"


def test_data_tree_widget_container_initialization(tree_widget_container):
    assert isinstance(tree_widget_container.search_bar, QtWidgets.QLineEdit)
    assert isinstance(tree_widget_container.btn_sort, QtWidgets.QPushButton)
    assert isinstance(tree_widget_container.data_tree, DataTreeWidget)


def test_data_tree_widget_container_set_data(tree_widget_container, sample_data):
    tree_widget_container.set_data(sample_data)
    root = tree_widget_container.data_tree.invisibleRootItem()
    assert root.childCount() == 3
    tree_widget_container.clear()
    assert root.childCount() == 0


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
