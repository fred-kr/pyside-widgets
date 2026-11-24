from collections.abc import Callable
from enum import Enum
from typing import Final
from warnings import deprecated

from PySide6.QtCore import Property, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QWidget

ItemDataRole = Qt.ItemDataRole

NO_SELECTION_TEXT: Final = "<No Selection>"


class EnumComboBox[T: Enum](QComboBox):
    """
    QComboBox populated from a python Enum class.

    The rows are owned by the widget: fill it with ``set_enum_class``, not with ``addItem``.

    Inspired by [`superqt.QEnumComboBox`](https://pyapp-kit.github.io/superqt/widgets/qenumcombobox/#qenumcombobox).
    """

    sig_current_enum_changed = Signal(object)
    """Emitted with the selected enum member, or None when nothing (or the "no selection" row) is selected."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        enum_class: type[T] | None = None,
        allow_none: bool = False,
    ) -> None:
        super().__init__(parent)

        self._enum_class: type[T] | None = None
        self._allow_none = allow_none
        self._text_data: Callable[[T], str] | None = None
        self._icon_data: Callable[[T], QIcon] | None = None
        self._doc_data: Callable[[T], str] | None = None

        # Row -> member, None for the "no selection" row. Kept in python because Qt stores a str or int subclass
        # (StrEnum, IntEnum) as a plain QString / int, which loses the member.
        self._members: list[T | None] = []
        self._last_emitted: T | None = None
        self._rebuilding = False

        self.currentIndexChanged.connect(self._on_current_index_changed)
        self.set_enum_class(enum_class)

    def get_allow_none(self) -> bool:
        """Whether the combo box offers a "no selection" row."""
        return self._allow_none

    @Slot(bool)
    def set_allow_none(self, allow_none: bool) -> None:
        """Add or remove the "no selection" row. The current member stays selected where possible."""
        if allow_none == self._allow_none:
            return
        self._allow_none = allow_none
        self._rebuild_items()

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
        """Repopulate the rows, keep the current member if it still exists, and emit at most one change signal."""
        previous = self.get_current_enum()
        self._rebuilding = True
        try:
            self.clear()
            self._members = []
            if self._enum_class is not None:
                if self._allow_none:
                    self._add_row(None, self.tr(NO_SELECTION_TEXT))
                for member in self._enum_class:
                    self._add_row(member, self._text_data(member) if self._text_data is not None else member.name)
            keep = next((row for row, member in enumerate(self._members) if member is previous), 0)
            self.setCurrentIndex(keep if self._members else -1)
        finally:
            self._rebuilding = False
        self._emit_if_changed()

    def _add_row(self, member: T | None, text: str) -> None:
        self._members.append(member)
        self.addItem(text, member)  # also as item data, so currentData() and findData() keep working
        if member is None:
            return
        row = self.count() - 1
        if self._icon_data is not None:
            self.setItemIcon(row, self._icon_data(member))
        if self._doc_data is not None:
            self.setItemData(row, self._doc_data(member), ItemDataRole.ToolTipRole)

    def get_current_enum(self) -> T | None:
        """The selected enum member, or None if nothing or the "no selection" row is selected."""
        row = self.currentIndex()
        return self._members[row] if 0 <= row < len(self._members) else None

    def set_current_enum(self, value: T | None) -> None:
        """
        Select ``value``.

        Besides a member, the plain value of a member is accepted (``3`` for ``Color.BLUE``). That is what arrives
        when a member has travelled through Qt, for example from ``QSettings`` or an item model.

        Raises:
            ValueError: If no enum class is set, ``value`` is None while ``allowNone`` is False, or ``value`` is
                neither a member of the enum class nor the value of one.
        """
        if self._enum_class is None:
            raise ValueError("Enum class not set")
        if value is None:
            if not self._allow_none:
                raise ValueError("Cannot set None if allow_none is False")
            self.setCurrentIndex(0)
            return
        try:
            member = value if isinstance(value, self._enum_class) else self._enum_class(value)
        except ValueError:
            raise ValueError(f"{value!r} is not a member of {self._enum_class.__name__}") from None
        self.setCurrentIndex(self._members.index(member))

    @Slot(int)
    def _on_current_index_changed(self, index: int) -> None:
        if not self._rebuilding:
            self._emit_if_changed()

    def _emit_if_changed(self) -> None:
        current = self.get_current_enum()
        if current is not self._last_emitted:
            self._last_emitted = current
            self.sig_current_enum_changed.emit(current)

    @deprecated("Use get_current_enum() or the currentEnum property. Removed in 0.6.")
    def current_enum(self) -> T | None:
        return self.get_current_enum()

    allowNone = Property(bool, get_allow_none, set_allow_none)
    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setAllowNone = set_allow_none
    # "QVariant" rather than object: an object-typed property rejects the int or str a member turns into inside Qt.
    # PySide6 accepts the type name as a string; its stubs only declare `type`.
    currentEnum = Property(
        "QVariant",  # pyright: ignore[reportArgumentType]
        get_current_enum,
        set_current_enum,
        notify=sig_current_enum_changed,
        user=True,
        designable=False,
    )
