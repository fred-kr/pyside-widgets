from PySide6.QtCore import Property, QSize, Qt
from PySide6.QtGui import QAction, QActionEvent, QResizeEvent
from PySide6.QtWidgets import QToolBar, QWidget


class CommandBar(QToolBar):
    """
    Non-movable toolbar with text under icons whose buttons either fill the width evenly or align to one side.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        fill: bool = True,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(16, 16))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self._fill = fill
        self._alignment = alignment

    def set_fill(self, fill: bool) -> None:
        """When True, buttons are stretched to fill the toolbar. When False, they keep their size hint."""
        if fill != self._fill:
            self._fill = fill
            self._relayout()

    def get_fill(self) -> bool:
        return self._fill

    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        """Side the buttons are packed to when ``fill`` is False. Only AlignLeft and AlignRight are distinguished."""
        if alignment != self._alignment:
            self._alignment = alignment
            self._relayout()

    def get_alignment(self) -> Qt.AlignmentFlag:
        return self._alignment

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._relayout()

    def actionEvent(self, event: QActionEvent) -> None:
        super().actionEvent(event)
        self._relayout()

    def _relayout(self) -> None:
        actions = self.actions()
        if not actions:
            return
        if self._fill:
            self._layout_fill(actions)
        else:
            self._layout_align(actions)

    def _layout_align(self, actions: list[QAction]) -> None:
        widgets = [(w, w.sizeHint().width()) for a in actions if (w := self.widgetForAction(a)) is not None]
        required = sum(width for _, width in widgets)

        x = 0
        if required <= self.width() and self._alignment == Qt.AlignmentFlag.AlignRight:
            x = self.width() - required
        for widget, width in widgets:
            widget.setGeometry(x, 0, width, self.height())
            x += width

    def _layout_fill(self, actions: list[QAction]) -> None:
        widgets = [(a, w) for a in actions if (w := self.widgetForAction(a)) is not None]
        separator_width = sum(w.sizeHint().width() for a, w in widgets if a.isSeparator())
        n_buttons = sum(1 for a, _ in widgets if not a.isSeparator())

        remaining = self.width() - separator_width
        if remaining < 0:
            remaining = self.width()
        base_width, remainder = divmod(remaining, n_buttons) if n_buttons else (0, 0)

        x = 0
        for action, widget in widgets:
            if action.isSeparator():
                width = widget.sizeHint().width()
            else:
                width = base_width + (1 if remainder > 0 else 0)
                remainder -= 1
            widget.setGeometry(x, 0, width, self.height())
            x += width

    fill = Property(bool, get_fill, set_fill)
    alignment = Property(Qt.AlignmentFlag, get_alignment, set_alignment)
