from PySide6 import QtCore, QtGui, QtWidgets

import pyside_widgets.rc_resources  # noqa: F401  # type: ignore


def draw_icon(
    icon: QtGui.QIcon | QtGui.QPixmap,
    painter: QtGui.QPainter,
    rect: QtCore.QRectF,
    state: QtGui.QIcon.State = QtGui.QIcon.State.Off,
) -> None:
    icon = QtGui.QIcon(icon)
    icon.paint(painter, QtCore.QRectF(rect).toRect(), QtCore.Qt.AlignmentFlag.AlignCenter, state=state)


class CommandBar(QtWidgets.QToolBar):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QtCore.QSize(16, 16))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        actions = self.actions()
        if not actions:
            return

        # Gather non-separator actions.
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        num_non_separator = len(non_separator_actions)

        # Calculate the total width required by separator widgets using their sizeHint.
        separator_total_width = 0
        for action in actions:
            if action.isSeparator():
                if widget := self.widgetForAction(action):
                    separator_total_width += widget.sizeHint().width()

        total_width = self.width()
        # Width available for non-separator actions.
        remaining_width = total_width - separator_total_width
        if remaining_width < 0:
            remaining_width = total_width  # Fallback in case separators exceed total width.

        # Determine base width for each non-separator action.
        base_width = remaining_width // num_non_separator if num_non_separator > 0 else 0
        remainder = remaining_width % num_non_separator if num_non_separator > 0 else 0

        x = 0
        for action in actions:
            widget = self.widgetForAction(action)
            if not widget:
                continue

            if action.isSeparator():
                # Use the size hint for separators.
                w = widget.sizeHint().width()
            else:
                # Add any remainder pixels one-by-one to the first few buttons.
                w = base_width + (1 if remainder > 0 else 0)
                if remainder > 0:
                    remainder -= 1

            widget.setGeometry(x, 0, w, self.height())
            x += w
