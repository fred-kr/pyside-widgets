# from PySide6 import QtCore, QtGui, QtWidgets


# class CommandBar(QtWidgets.QToolBar):
#     def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
#         super().__init__(parent)
#         self.setMovable(False)
#         self.setIconSize(QtCore.QSize(16, 16))
#         self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

#     def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
#         super().resizeEvent(event)
#         actions = self.actions()
#         if not actions:
#             return

#         # Gather visible non-separator actions
#         non_separator_actions = [a for a in actions if not a.isSeparator()]
#         num_non_separator = len(non_separator_actions)

#         # Calculate the total width required by separator widgets using their sizeHint.
#         separator_total_width = 0
#         for action in actions:
#             if action.isSeparator():
#                 if widget := self.widgetForAction(action):
#                     separator_total_width += widget.sizeHint().width()

#         total_width = self.width()
#         # Width available for non-separator actions.
#         remaining_width = total_width - separator_total_width
#         if remaining_width < 0:
#             remaining_width = total_width  # Fallback in case separators exceed total width.

#         # Determine base width for each non-separator action.
#         base_width = remaining_width // num_non_separator if num_non_separator > 0 else 0
#         remainder = remaining_width % num_non_separator if num_non_separator > 0 else 0

#         x = 0
#         for action in actions:
#             widget = self.widgetForAction(action)
#             if not widget:
#                 continue

#             if action.isSeparator():
#                 # Use the size hint for separators.
#                 w = widget.sizeHint().width()
#             else:
#                 # Add any remainder pixels one-by-one to the first few buttons.
#                 w = base_width + (1 if remainder > 0 else 0)
#                 if remainder > 0:
#                     remainder -= 1

#             widget.setGeometry(x, 0, w, self.height())
#             x += w
from PySide6 import QtCore, QtGui, QtWidgets


class CommandBar(QtWidgets.QToolBar):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        fill: bool = True,
        alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QtCore.QSize(16, 16))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # When fill is True the actions will be stretched to fill the toolbar.
        # When fill is False the actions will use their sizeHint, and be aligned according to _alignment.
        self._fill = fill
        self._alignment = alignment

    def setFill(self, fill: bool) -> None:
        """Enable or disable filling the toolbar with evenly distributed buttons."""
        self._fill = fill
        self.update()

    def setAlignment(self, alignment: QtCore.Qt.AlignmentFlag) -> None:
        """Set the alignment (e.g. Qt.AlignLeft or Qt.AlignRight) for non-fill mode."""
        self._alignment = alignment
        self.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        actions = self.actions()
        if not actions:
            return

        total_width = self.width()

        if self._fill:
            # --- FILL MODE: Evenly distribute non-separator actions across the full width ---
            non_separator_actions = [a for a in actions if not a.isSeparator()]
            num_non_separator = len(non_separator_actions)

            # Calculate the total fixed width taken by separator widgets.
            separator_total_width = 0
            for action in actions:
                if action.isSeparator():
                    if widget := self.widgetForAction(action):
                        separator_total_width += widget.sizeHint().width()

            remaining_width = total_width - separator_total_width
            if remaining_width < 0:
                remaining_width = total_width  # Fallback if separators exceed total width

            base_width = remaining_width // num_non_separator if num_non_separator > 0 else 0
            remainder = remaining_width % num_non_separator if num_non_separator > 0 else 0

            x = 0
            for action in actions:
                widget = self.widgetForAction(action)
                if not widget:
                    continue

                if action.isSeparator():
                    w = widget.sizeHint().width()
                else:
                    # Distribute any extra pixel(s) to the first few non-separator buttons.
                    w = base_width + (1 if remainder > 0 else 0)
                    if remainder > 0:
                        remainder -= 1

                widget.setGeometry(x, 0, w, self.height())
                x += w

        else:
            # --- NON-FILL MODE: Use each widget's natural size and align the group ---
            # First, compute the total width required by the visible widgets.
            total_required_width = 0
            widget_geometries: list[tuple[QtWidgets.QWidget, int]] = []  # Store tuples of (widget, width)
            for action in actions:
                widget = self.widgetForAction(action)
                if not widget:
                    continue
                w = widget.sizeHint().width()
                widget_geometries.append((widget, w))
                total_required_width += w

            # Determine starting x based on alignment.
            if total_required_width > total_width:
                # If actions exceed available width, simply start at 0.
                start_x = 0
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignRight:
                start_x = total_width - total_required_width
            else:
                # Default to left alignment.
                start_x = 0

            x = start_x
            for widget, w in widget_geometries:
                widget.setGeometry(x, 0, w, self.height())
                x += w


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    command_bar = CommandBar()
    icons = [
        QtGui.QIcon.fromTheme("edit-copy"),
        QtGui.QIcon.fromTheme("edit-paste"),
        QtGui.QIcon.fromTheme("edit-delete"),
    ]
    actions = [
        QtGui.QAction("long Action 1", icon=icons[0]),
        QtGui.QAction("Action 2", icon=icons[1]),
        QtGui.QAction("Action 3", icon=icons[2]),
    ]
    command_bar.addActions(actions)
    command_bar.setFill(False)
    command_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    command_bar.show()
    sys.exit(app.exec())
