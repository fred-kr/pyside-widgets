import math
import traceback
import types
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QAction, QContextMenuEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    import numpy.typing as npt

ItemDataRole = Qt.ItemDataRole

_MAX_INLINE_ELEMENTS = 1000
"""Arrays with more elements than this get a summary button instead of an inline table."""
_MAX_TABLE_CELLS = 10_000
"""Upper bound on cells rendered in any array table, inline or in the full-array dialog."""
_MAX_DESC_LENGTH = 100
"""Longer value descriptions are truncated in the tree and shown in full in a child text box."""


def _is_array_like(obj: object) -> bool:
    """True for numpy arrays and anything with the same ``shape``/``dtype``/``__array__`` interface."""
    return hasattr(obj, "__array__") and hasattr(obj, "shape") and hasattr(obj, "dtype")


def _array_size(arr: Any) -> int:
    size = getattr(arr, "size", None)
    return int(size) if size is not None else math.prod(arr.shape)


def _children(item: QTreeWidgetItem) -> Iterator[QTreeWidgetItem]:
    for row in range(item.childCount()):
        child = item.child(row)
        if child is not None:
            yield child


def _array_table(arr: Any, parent: QWidget | None = None) -> QWidget:
    """Read-only table showing a 0-, 1- or 2-d array. Higher dimensions fall back to text."""
    shape = tuple(arr.shape)
    if len(shape) > 2:
        editor = QPlainTextEdit(str(arr), parent)
        editor.setReadOnly(True)
        return editor

    n_cols = shape[1] if len(shape) == 2 else 1
    n_rows = min(shape[0] if shape else 1, _MAX_TABLE_CELLS // max(n_cols, 1))

    if len(shape) == 0:
        rows: list[list[Any]] = [[arr.tolist()]]
    elif len(shape) == 1:
        rows = [[v] for v in arr[:n_rows].tolist()]
    else:
        rows = arr[:n_rows].tolist()

    table = QTableWidget(n_rows, n_cols, parent)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(str(value)))
    return table


class DataTreeWidget(QTreeWidget):
    """
    Tree view of nested python data (dicts, lists, tuples, arrays, tracebacks, scalars).

    Based on `pyqtgraph.widgets.DataTreeWidget`, without the pyqtgraph/numpy dependency.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        data: Any = None,
        allow_edit: bool = False,
        hide_root: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setColumnCount(3)
        self.setHeaderLabels([self.tr("Name"), self.tr("Type"), self.tr("Value")])
        self.setAlternatingRowColors(True)

        self._allow_edit = allow_edit
        self._sort_order: Qt.SortOrder | None = None
        self._widgets: list[QWidget] = []

        if data is not None:
            self.set_data(data, hide_root=hide_root)

    def clear(self) -> None:
        super().clear()
        self._widgets.clear()

    def set_data(self, data: Any, hide_root: bool = True) -> None:
        """
        Replace the displayed data.

        Args:
            data: The data to display.
            hide_root: If True, the top-level entries of ``data`` become top-level tree items. If False, a single
                root item wraps them.
        """
        self.clear()
        self.build_tree(data, self.invisibleRootItem(), hide_root=hide_root)
        self.expandToDepth(3)
        self.resizeColumnToContents(0)

    def build_tree(self, data: Any, parent: QTreeWidgetItem, name: str = "", hide_root: bool = True) -> None:
        """Recursively add ``data`` below ``parent``."""
        if hide_root:
            node = parent
        else:
            node = QTreeWidgetItem([name, "", ""])
            parent.addChild(node)

        type_str, desc, childs, widget = self.parse_data(data)

        node.setText(1, type_str)
        node.setData(2, ItemDataRole.UserRole, data)

        if len(desc) > _MAX_DESC_LENGTH:
            node.setText(2, f"{desc[: _MAX_DESC_LENGTH - 3]}...")
            if widget is None:
                widget = QPlainTextEdit(desc)
                widget.setReadOnly(True)
                widget.setMaximumHeight(200)
        else:
            node.setText(2, desc)

        if widget is not None:
            self._widgets.append(widget)
            sub_node = QTreeWidgetItem(["", "", ""])
            node.addChild(sub_node)
            self.setItemWidget(sub_node, 0, widget)
            sub_node.setFirstColumnSpanned(True)

        for key, child_data in childs.items():
            self.build_tree(child_data, node, str(key), hide_root=False)

    def parse_data(self, data: Any) -> tuple[str, str, dict[Any, Any], QWidget | None]:
        """
        Describe ``data`` for display.

        Returns:
            type name, description text, children to recurse into, and an optional widget that shows the value.
        """
        type_str = type(data).__name__
        widget: QWidget | None = None
        desc = ""
        childs: dict[Any, Any] = {}

        if isinstance(data, dict):
            desc = f"length={len(data)}"
            childs = dict(data)
        elif isinstance(data, (list, tuple)):
            desc = f"length={len(data)}"
            childs = dict(enumerate(data))
        elif _is_array_like(data):
            desc, widget = self._parse_array(data)
        elif isinstance(data, types.TracebackType):
            frames = [frame.strip() for frame in traceback.format_list(traceback.extract_tb(data))]
            widget = QPlainTextEdit("\n".join(frames))
            widget.setMaximumHeight(200)
            widget.setReadOnly(True)
        else:
            desc = str(data)

        return type_str, desc, childs, widget

    def _parse_array(self, data: Any) -> tuple[str, QWidget | None]:
        desc = f"shape={tuple(data.shape)} dtype={data.dtype}"
        if _array_size(data) <= _MAX_INLINE_ELEMENTS:
            table = _array_table(data)
            table.setMaximumHeight(200)
            return desc, table

        try:
            summary = f"min={data.min()}, max={data.max()}, mean={float(data.mean()):.2f}"
        except TypeError, ValueError:
            summary = f"{_array_size(data)} elements"
        button = QPushButton(self.tr("Array summary: {}").format(summary))
        button.clicked.connect(lambda: self.show_full_array(data))
        return desc, button

    @Slot(str)
    def filter_tree(self, text: str) -> None:
        """
        Show only the items whose name contains ``text`` (case-insensitive).

        A matching item stays reachable and complete: its ancestors and everything below it are shown too. An empty
        ``text`` shows every item.
        """
        needle = text.lower()
        for item in _children(self.invisibleRootItem()):
            self._apply_filter(item, needle, ancestor_matches=False)

    def _apply_filter(self, item: QTreeWidgetItem, needle: str, ancestor_matches: bool) -> bool:
        """Set the visibility of ``item`` and its descendants. Returns whether ``item`` is visible."""
        matches = ancestor_matches or needle in item.text(0).lower()
        visible = matches
        for child in _children(item):
            # No short-circuit: every child must be visited even after one of them matched.
            visible |= self._apply_filter(child, needle, matches)
        item.setHidden(not visible)
        return visible

    @Slot()
    def toggle_sort(self) -> None:
        """Sort by name. The first call sorts ascending; later calls alternate the direction."""
        if self._sort_order == Qt.SortOrder.AscendingOrder:
            self._sort_order = Qt.SortOrder.DescendingOrder
        else:
            self._sort_order = Qt.SortOrder.AscendingOrder
        self.sortItems(0, self._sort_order)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        # An override instead of a connection to customContextMenuRequested, so an application can still set its own
        # context menu policy on this widget.
        self.show_context_menu(event.pos())

    def show_context_menu(self, pos: QPoint) -> None:
        """Show the copy/edit menu for the item at ``pos`` (viewport coordinates). Does nothing over empty space."""
        item = self.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        clipboard = QApplication.clipboard()
        labels = (self.tr("Copy Name"), self.tr("Copy Type"), self.tr("Copy Value"))
        for column, label in enumerate(labels):
            action = QAction(label, menu)
            action.triggered.connect(lambda _=False, col=column: clipboard.setText(item.text(col)))
            menu.addAction(action)

        if self._allow_edit:
            edit_action = QAction(self.tr("Edit Value"), menu)
            edit_action.triggered.connect(lambda: self.edit_item_value(item))
            menu.addAction(edit_action)

        menu.exec(self.viewport().mapToGlobal(pos))

    def edit_item_value(self, item: QTreeWidgetItem) -> None:
        """
        Prompt for a new scalar value (int, float, str or bool) and store it on ``item``.

        Only the tree item changes. The object passed to ``set_data`` is not modified and no signal is emitted.
        """
        if not self._allow_edit:
            return
        data = item.data(2, ItemDataRole.UserRole)
        if not isinstance(data, (int, float, str, bool)):
            return

        new_value, ok = QInputDialog.getText(self, self.tr("Edit Value"), self.tr("Enter new value:"), text=str(data))
        if not ok:
            return
        try:
            if isinstance(data, bool):
                new_data: Any = new_value.lower() in ("true", "1", "yes")
            else:
                new_data = type(data)(new_value)
        except ValueError:
            QMessageBox.warning(self, self.tr("Invalid Input"), self.tr("Could not convert input to correct type"))
            return

        item.setData(2, ItemDataRole.UserRole, new_data)
        item.setText(2, str(new_data))

    def show_full_array(self, data: npt.ArrayLike) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Array"))
        layout = QVBoxLayout(dialog)
        layout.addWidget(_array_table(data, dialog))
        dialog.resize(600, 400)
        dialog.exec()


class SearchableDataTreeWidget(QWidget):
    """``DataTreeWidget`` with a search box and a sort button above it."""

    def __init__(self, parent: QWidget | None = None, *, allow_edit: bool = False) -> None:
        super().__init__(parent)

        self.data_tree = DataTreeWidget(self, allow_edit=allow_edit)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText(self.tr("Search..."))
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.data_tree.filter_tree)

        self.btn_sort = QPushButton(self.tr("Sort"), self)
        self.btn_sort.clicked.connect(self.data_tree.toggle_sort)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.btn_sort)
        layout.addWidget(self.data_tree)

    def filter_tree(self, text: str) -> None:
        self.data_tree.filter_tree(text)

    def toggle_sort(self) -> None:
        self.data_tree.toggle_sort()

    def set_data(self, data: Any, hide_root: bool = True) -> None:
        self.data_tree.set_data(data, hide_root)

    def collapseAll(self) -> None:
        self.data_tree.collapseAll()

    def clear(self) -> None:
        self.data_tree.clear()
