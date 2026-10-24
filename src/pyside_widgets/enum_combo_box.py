from collections.abc import Callable
from enum import Enum
from typing import Final

from PySide6.QtCore import Property, Qt, Signal, Slot
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QWidget

ItemDataRole = Qt.ItemDataRole

PLACEHOLDER_TEXT: Final = "Select..."
NO_SELECTION_TEXT: Final = "<No Selection>"


class EnumComboBox[T: Enum](QComboBox):
    """
    QComboBox populated from a python Enum class.

    Inspired by [`superqt.QEnumComboBox`](https://pyapp-kit.github.io/superqt/widgets/qenumcombobox/#qenumcombobox).
    """

    sig_current_enum_changed = Signal(object)
    """Emitted with the selected enum member, or None when nothing (or the "no selection" row) is selected."""

    def __init__(
        self,
        parent: QWidget | None = None,
        enum_class: type[T] | None = None,
        allow_none: bool = False,
    ) -> None:
        super().__init__(parent)

        self._enum_class: type[T] | None = None
        self._allow_none = allow_none
        self._text_data: Callable[[T], str] | None = None
        self._icon_data: Callable[[T], QIcon] | None = None
        self._doc_data: Callable[[T], str] | None = None

        self._enum_model = QStandardItemModel(self)
        self.setModel(self._enum_model)
        self.setPlaceholderText(PLACEHOLDER_TEXT)

        self.set_enum_class(enum_class)
        self.currentIndexChanged.connect(self._on_current_index_changed)

    def allowNone(self) -> bool:
        """Whether the combo box offers a "no selection" row."""
        return self._allow_none

    def setAllowNone(self, allow_none: bool) -> None:
        """Setter of property `allowNone`. Rebuilds the items and keeps the current selection where possible."""
        if allow_none == self._allow_none:
            return
        self._allow_none = allow_none
        current = self.current_enum()
        self._rebuild_items()
        if current is not None:
            self.set_current_enum(current)

    def set_enum_class(
        self,
        enum_class: type[T] | None,
        text_data: Callable[[T], str] | None = None,
        icon_data: Callable[[T], QIcon] | None = None,
        doc_data: Callable[[T], str] | None = None,
    ) -> None:
        """
        Set the enum class and populate the combo box with its members.

        Args:
            enum_class: The enum class to show. None clears the combo box.
            text_data: Returns the display text for a member. Defaults to the member name.
            icon_data: Returns an icon for a member. Defaults to no icon.
            doc_data: Returns the tooltip for a member. Defaults to no tooltip.
        """
        self._enum_class = enum_class
        self._text_data = text_data
        self._icon_data = icon_data
        self._doc_data = doc_data
        self._rebuild_items()

    def _rebuild_items(self) -> None:
        self._enum_model.clear()
        if self._enum_class is None:
            return

        if self._allow_none:
            none_item = QStandardItem(NO_SELECTION_TEXT)
            none_item.setData(None, role=ItemDataRole.UserRole)
            self._enum_model.appendRow(none_item)

        for member in self._enum_class:
            item = QStandardItem(self._text_data(member) if self._text_data is not None else member.name)
            item.setData(member, role=ItemDataRole.UserRole)
            if self._icon_data is not None:
                item.setIcon(self._icon_data(member))
            if self._doc_data is not None:
                item.setToolTip(self._doc_data(member))
            self._enum_model.appendRow(item)

        # QComboBox does not auto-select the first row while placeholder text is set; select it explicitly so the
        # combo box always has a current member (or the "no selection" row) once populated.
        if self.currentIndex() < 0 and self.count() > 0:
            self.setCurrentIndex(0)

    def current_enum(self) -> T | None:
        """The selected enum member, or None if nothing or the "no selection" row is selected."""
        if self._enum_class is None:
            return None
        data = self.currentData(role=ItemDataRole.UserRole)
        if data is None or isinstance(data, self._enum_class):
            return data
        # Qt stores a str or int subclass (StrEnum, IntEnum) as a plain QString / int; map it back to the member.
        try:
            return self._enum_class(data)
        except ValueError:
            return None

    def set_current_enum(self, value: T | None) -> None:
        """
        Select ``value``.

        Raises:
            ValueError: If no enum class is set, or ``value`` is None while ``allowNone`` is False.
        """
        if self._enum_class is None:
            raise ValueError("Enum class not set")
        if value is None:
            if not self._allow_none:
                raise ValueError("Cannot set None if allow_none is False")
            self.setCurrentIndex(0)
            return
        index = self.findData(value, role=ItemDataRole.UserRole)
        if index >= 0:
            self.setCurrentIndex(index)

    @Slot(int)
    def _on_current_index_changed(self, index: int) -> None:
        self.sig_current_enum_changed.emit(self.current_enum())

    allowNone = Property(bool, allowNone, setAllowNone)  # type: ignore[assignment]
