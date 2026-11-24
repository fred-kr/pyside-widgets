import enum
from typing import Any, cast

from PySide6.QtCore import QEvent, QModelIndex, QObject, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPalette, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

ItemDataRole = Qt.ItemDataRole

ItemTypeRole = ItemDataRole.UserRole + 1

type ModelIndex = QModelIndex | QPersistentModelIndex


class ItemType(enum.Enum):
    SEPARATOR = enum.auto()
    PARENT = enum.auto()
    CHILD = enum.auto()


class GroupedComboBox(QComboBox):
    """
    A QComboBox whose items are grouped under bold, non-selectable headers.

    Headers and separators can never become the current item through the popup, the keyboard or the mouse wheel.
    ``currentData()`` and the other ``QComboBox`` accessors behave as in the base class. Known limitation: a view set
    with ``setView()`` loses the protection against clicks on headers.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.setItemDelegate(GroupedComboBoxDelegate(self))
        # Installed after the popup's own filter, so it runs first.
        self.view().viewport().installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and watched is self.view().viewport()
        ):
            # The popup selects the row that was last hovered, wherever the button is released. Over a header or a
            # separator that would pick a neighbouring item, so the release is swallowed and the popup stays open.
            index = self.view().indexAt(event.position().toPoint())
            if index.isValid() and not (index.flags() & Qt.ItemFlag.ItemIsSelectable):
                return True
        return super().eventFilter(watched, event)

    def add_separator(self) -> None:
        """Add a thin horizontal line."""
        item = QStandardItem()
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setData(ItemType.SEPARATOR, ItemTypeRole)
        self._append(item)

    def add_parent_item(self, text: str) -> None:
        """
        Add a group header.

        Args:
            text: The header text, shown in bold.
        """
        item = QStandardItem(text)
        # Not enabled, so that keyboard and wheel navigation in the closed combo box skip the header. The delegate
        # still paints it with the enabled palette.
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setData(ItemType.PARENT, ItemTypeRole)

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        self._append(item)

    def add_child_item(self, text: str, data: Any = None) -> None:
        """
        Add a selectable item, indented below the most recent header.

        Args:
            text: The item text.
            data: Returned by ``currentData()`` while the item is selected.
        """
        item = QStandardItem(text)
        item.setData(data, ItemDataRole.UserRole)
        item.setData(ItemType.CHILD, ItemTypeRole)
        self._append(item)

    def _append(self, item: QStandardItem) -> None:
        self._model.appendRow(item)
        # QComboBox makes the first inserted row current, even a header. Move on to the first selectable row.
        if not self._is_selectable(self.currentIndex()):
            self.setCurrentIndex(next((row for row in range(self.count()) if self._is_selectable(row)), -1))

    def _is_selectable(self, row: int) -> bool:
        item = self._model.item(row) if row >= 0 else None
        return item is not None and item.isSelectable()


class GroupedComboBoxDelegate(QStyledItemDelegate):
    """Paints separators as lines, headers on a tinted background and child items indented."""

    _CHILD_INDENT = 20
    _SEPARATOR_HEIGHT = 5

    def sizeHint(self, option: QStyleOptionViewItem, index: ModelIndex) -> QSize:
        if index.data(ItemTypeRole) == ItemType.SEPARATOR:
            return QSize(0, self._SEPARATOR_HEIGHT)
        return super().sizeHint(option, index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: ModelIndex) -> None:
        item_type = index.data(ItemTypeRole)
        # The PySide6 stubs declare the fields of QStyleOption without a type, hence the casts.
        rect = cast(QRect, option.rect)
        palette = cast(QPalette, option.palette)

        if item_type == ItemType.SEPARATOR:
            y = rect.center().y()
            painter.save()
            painter.setPen(palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark))
            painter.drawLine(rect.left(), y, rect.right(), y)
            painter.restore()
            return

        # Work on a copy: the view reuses the option it passes in for the next row.
        own = QStyleOptionViewItem(option)
        if item_type == ItemType.PARENT:
            painter.fillRect(rect, palette.midlight())
            state = cast(QStyle.StateFlag, own.state) | QStyle.StateFlag.State_Enabled
            own.state = state & ~(QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver)
        elif item_type == ItemType.CHILD:
            own.rect = rect.adjusted(self._CHILD_INDENT, 0, 0, 0)
        super().paint(painter, own, index)
