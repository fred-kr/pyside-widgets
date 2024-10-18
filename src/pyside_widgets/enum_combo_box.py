import enum
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

ItemDataRole = QtCore.Qt.ItemDataRole

class EnumComboBox[T: enum.Enum](QtWidgets.QComboBox):
    """
    QComboBox variant that uses the provided python Enum class to populate the combo box items.

    Inspired by [`superqt.QEnumComboBox`](https://pyapp-kit.github.io/superqt/widgets/qenumcombobox/#qenumcombobox).
    """    
    sig_current_enum_changed = QtCore.Signal(enum.Enum)

    def __init__(self, enum_class: t.Type[T], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self._enum_model = QtGui.QStandardItemModel(self)

        self.set_enum_class(enum_class)
        self.currentIndexChanged.connect(self._on_current_index_changed)

    def set_enum_class(
        self,
        enum_class: t.Type[T],
        text_data: t.Callable[[T], str] | None = None,
        icon_data: t.Callable[[T], QtGui.QIcon] | None = None,
    ) -> None:
        """
        Sets the enum class for the combo box and populates it with the enum members.

        :param enum_class: The enum class to be used in the combo box.
        :type enum_class: Type[T]
        :param text_data: Optional callable to provide custom text for each enum member. Defaults to None.
        :type text_data: Callable[[T], str] | None, optional
        :param icon_data: Optional callable to provide custom icon for each enum member. Defaults to None.
        :type icon_data: Callable[[T], QtGui.QIcon] | None, optional
        :return: None
        :rtype: None
        """
        self._enum_model.clear()

        for enum_member in enum_class:
            name = text_data(enum_member) if text_data is not None else enum_member.name
            item = QtGui.QStandardItem(name)
            item.setData(enum_member, role=ItemDataRole.UserRole)
            if icon_data is not None:
                item.setIcon(icon_data(enum_member))
            self._enum_model.appendRow(item)

        self.setModel(self._enum_model)

    def current_enum(self) -> T | None:
        """
        Returns the currently selected enum value.

        This method retrieves the data associated with the current item in the combo box using the UserRole. If the data
        is not a member of the enum class, it returns None.

        :return: The current enum value if it exists in the enum class, otherwise None.
        :rtype: T | None
        """
        data = self.currentData(role=ItemDataRole.UserRole)
        return None if data not in self._enum_class else data

    def set_current_enum(self, value: T) -> None:
        """
        Sets the current combo box item to the provided enum member.

        :param value: The enum member to be set as the current item.
        :type value: T
        """
        index = self.findData(value, role=ItemDataRole.UserRole)
        if index >= 0:
            self.setCurrentIndex(index)

    @QtCore.Slot(int)
    def _on_current_index_changed(self, index: int) -> None:
        enum_member = self.current_enum()
        if enum_member is not None:
            self.sig_current_enum_changed.emit(enum_member)
