from typing import Iterable, Sequence

from PySide6 import QtCore, QtGui, QtWidgets


def set_font(
    widget: QtWidgets.QWidget, font_size: int = 14, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Normal
) -> None:
    font = widget.font()
    font.setPointSize(font_size)
    font.setWeight(weight)
    widget.setFont(font)


def draw_icon(
    icon: QtGui.QIcon | QtGui.QPixmap,
    painter: QtGui.QPainter,
    rect: QtCore.QRectF,
    state: QtGui.QIcon.State = QtGui.QIcon.State.Off,
) -> None:
    icon = QtGui.QIcon(icon)
    icon.paint(painter, QtCore.QRectF(rect).toRect(), QtCore.Qt.AlignmentFlag.AlignCenter, state=state)


class ToolButton(QtWidgets.QToolButton):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.isPressed = False
        self.isHover = False
        self.setIconSize(QtCore.QSize(16, 16))
        self.setIcon(QtGui.QIcon())
        set_font(self)

    def setIcon(self, icon: QtGui.QIcon | QtGui.QPixmap) -> None:
        self._icon = icon
        self.update()

    def icon(self) -> QtGui.QIcon:
        return QtGui.QIcon(self._icon)

    def mousePressEvent(self, arg__1: QtGui.QMouseEvent) -> None:
        self.isPressed = True
        super().mousePressEvent(arg__1)

    def mouseReleaseEvent(self, arg__1: QtGui.QMouseEvent) -> None:
        self.isPressed = False
        super().mouseReleaseEvent(arg__1)

    def enterEvent(self, arg__1: QtCore.QEvent) -> None:
        self.isHover = True
        self.update()

    def leaveEvent(self, arg__1: QtCore.QEvent) -> None:
        self.isHover = False
        self.update()

    def _drawIcon(
        self,
        icon: QtGui.QIcon | QtGui.QPixmap,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        state: QtGui.QIcon.State = QtGui.QIcon.State.Off,
    ) -> None:
        draw_icon(icon, painter, rect, state)


class CommandButton(ToolButton):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setCheckable(False)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        set_font(self, 12)

        self._text = ""
        self._action: QtGui.QAction | None = None
        self._isTight = False

    def setTight(self, tight: bool) -> None:
        self._isTight = tight
        self.update()

    def isTight(self) -> bool:
        return self._isTight

    def sizeHint(self) -> QtCore.QSize:
        if self.isIconOnly():
            return QtCore.QSize(36, 34) if self.isTight() else QtCore.QSize(48, 34)

        # Text width
        tw = self.fontMetrics().boundingRect(self.text()).width()

        style = self.toolButtonStyle()
        if style == QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon:
            return QtCore.QSize(tw + 47, 34)
        elif style == QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly:
            return QtCore.QSize(tw + 32, 34)

        return QtCore.QSize(tw + 32, 50)

    def isIconOnly(self) -> bool:
        if not self.text():
            return True

        return self.toolButtonStyle() in [
            QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly,
            QtCore.Qt.ToolButtonStyle.ToolButtonFollowStyle,
        ]

    def _drawIcon(
        self,
        icon: QtGui.QIcon | QtGui.QPixmap,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        state: QtGui.QIcon.State = QtGui.QIcon.State.Off,
    ) -> None:
        pass

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text
        self.update()

    def setAction(self, action: QtGui.QAction) -> None:
        self._action = action
        self._onActionChanged()

        self.clicked.connect(action.trigger)
        action.toggled.connect(self.setChecked)
        action.changed.connect(self._onActionChanged)

    def _onActionChanged(self) -> None:
        action = self.action()
        if action is None:
            return
        self.setIcon(action.icon())
        self.setText(action.text())
        self.setToolTip(action.toolTip())
        self.setEnabled(action.isEnabled())
        self.setCheckable(action.isCheckable())
        self.setChecked(action.isChecked())

    def action(self) -> QtGui.QAction | None:
        return self._action

    def paintEvent(self, arg__1: QtGui.QPaintEvent) -> None:
        super().paintEvent(arg__1)

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        if not self.isChecked():
            painter.setPen(QtCore.Qt.GlobalColor.black)
        else:
            painter.setPen(QtCore.Qt.GlobalColor.white)

        if not self.isEnabled():
            painter.setOpacity(0.43)
        elif self.isPressed:
            painter.setOpacity(0.63)

        # draw icon and text
        style = self.toolButtonStyle()
        iw, ih = self.iconSize().width(), self.iconSize().height()

        if self.isIconOnly():
            y = (self.height() - ih) / 2
            x = (self.width() - iw) / 2
            super()._drawIcon(self._icon, painter, QtCore.QRectF(x, y, iw, ih))
        elif style == QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly:
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, self.text())
        elif style == QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon:
            y = (self.height() - ih) / 2
            super()._drawIcon(self._icon, painter, QtCore.QRectF(11, y, iw, ih))

            rect = QtCore.QRectF(26, 0, self.width() - 26, self.height())
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.text())
        elif style == QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon:
            x = (self.width() - iw) / 2
            super()._drawIcon(self._icon, painter, QtCore.QRectF(x, 9, iw, ih))

            rect = QtCore.QRectF(0, ih + 13, self.width(), self.height() - ih - 13)
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop, self.text())


class MoreActionsButton(CommandButton):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setIcon(QtGui.QIcon("src/icons/MoreHorizontal.svg"))

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(40, 34)

    def clearState(self) -> None:
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_UnderMouse, False)
        e = QtGui.QHoverEvent(QtCore.QEvent.Type.HoverLeave, QtCore.QPoint(-1, -1), QtCore.QPoint())
        QtWidgets.QApplication.sendEvent(self, e)


class CommandSeparator(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFixedSize(9, 34)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QColor(0, 0, 0, 15))
        painter.drawLine(5, 2, 5, self.height() - 2)


class CommandBar(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._widgets: list[QtWidgets.QWidget] = []
        self._hidden_widgets: list[QtWidgets.QWidget] = []
        self._hidden_actions: list[QtGui.QAction] = []

        self._tool_button_style = QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly
        self._icon_size = QtCore.QSize(16, 16)
        self._tight_spacing = False
        self._spacing = 4

        self.btn_more = MoreActionsButton(self)
        self.btn_more.clicked.connect(self._showMoreActionsMenu)
        self.btn_more.hide()

        self.setFont(QtGui.QFont("Segoe UI", 12))
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    @property
    def command_buttons(self) -> list[CommandButton]:
        return [w for w in self._widgets if isinstance(w, CommandButton)]

    def setSpacing(self, spacing: int) -> None:
        if spacing == self._spacing:
            return

        self._spacing = spacing
        self.updateGeometry()

    def spacing(self) -> int:
        return self._spacing

    def addAction(self, action: QtGui.QAction) -> CommandButton | None:
        if action in self.actions():
            return

        btn = self._createButton(action)
        self._insertWidgetToLayout(-1, btn)
        super().addAction(action)
        return btn

    def addActions(self, actions: Iterable[QtGui.QAction]) -> None:
        for action in actions:
            self.addAction(action)

    def addHiddenAction(self, action: QtGui.QAction) -> None:
        if action in self.actions():
            return

        self._hidden_actions.append(action)
        self.updateGeometry()
        super().addAction(action)

    def addHiddenActions(self, actions: Iterable[QtGui.QAction]) -> None:
        for action in actions:
            self.addHiddenAction(action)

    def insertAction(self, before: QtGui.QAction, action: QtGui.QAction) -> CommandButton | None:
        if before not in self.actions():
            return

        index = self.actions().index(before)
        btn = self._createButton(action)
        self._insertWidgetToLayout(index, btn)
        super().insertAction(before, action)
        return btn

    def addSeparator(self) -> None:
        self.insertSeparator(-1)

    def insertSeparator(self, index: int) -> None:
        self._insertWidgetToLayout(index, CommandSeparator(self))

    def addWidget(self, widget: QtWidgets.QWidget) -> None:
        self._insertWidgetToLayout(-1, widget)

    def removeAction(self, action: QtGui.QAction):
        if agtion not in self.actions():
            return

        for w in self.command_buttons:
            if w.action() is action:
                self._widgets.remove(w)
                w.hide()
                w.deleteLater()
                break

        self.updateGeometry()

    def removeWidget(self, widget: QtWidgets.QWidget) -> None:
        if widget not in self._widgets:
            return

        self._widgets.remove(widget)
        self.updateGeometry()

    def removeHiddenAction(self, action: QtGui.QAction) -> None:
        if action in self._hidden_actions:
            self._hidden_actions.remove(action)

    def setToolButtonStyle(self, style: QtCore.Qt.ToolButtonStyle) -> None:
        if self.toolButtonStyle() == style:
            return

        self._tool_button_style = style
        for w in self.command_buttons:
            w.setToolButtonStyle(style)

    def toolButtonStyle(self) -> QtCore.Qt.ToolButtonStyle:
        return self._tool_button_style

    def setButtonTight(self, tight: bool) -> None:
        if self.isButtonTight() == tight:
            return

        self._tight_spacing = tight
        for w in self.command_buttons:
            w.setTight(tight)

        self.updateGeometry()

    def isButtonTight(self) -> bool:
        return self._tight_spacing

    def setIconSize(self, size: QtCore.QSize) -> None:
        if self.iconSize() == size:
            return

        self._icon_size = size
        for w in self.command_buttons:
            w.setIconSize(size)

    def iconSize(self) -> QtCore.QSize:
        return self._icon_size

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.updateGeometry()

    def _createButton(self, action: QtGui.QAction) -> CommandButton:
        btn = CommandButton(self)
        btn.setAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        btn.setTight(self.isButtonTight())
        btn.setIconSize(self.iconSize())
        btn.setFont(self.font())
        return btn

    def _insertWidgetToLayout(self, index: int, widget: QtWidgets.QWidget) -> None:
        widget.setParent(self)
        widget.show()

        if index < 0:
            self._widgets.append(widget)
        else:
            self._widgets.insert(index, widget)

        self.setFixedHeight(max(w.height() for w in self._widgets))

        self.updateGeometry()

    def minimumSizeHint(self) -> QtCore.QSize:
        return self.btn_more.size()

    def updateGeometry(self) -> None:
        self._hidden_widgets.clear()
        self.btn_more.hide()

        visibles = self._visibleWidgets()
        x = self.contentsMargins().left()
        h = self.height()

        for widget in visibles:
            widget.show()
            widget.move(x, (h - widget.height()) // 2)
            x += widget.width() + self.spacing()

        if self._hidden_actions or len(visibles) < len(self._widgets):
            self.btn_more.show()
            self.btn_more.move(x, (h - self.btn_more.height()) // 2)

        for widget in self._widgets[len(visibles) :]:
            widget.hide()
            self._hidden_widgets.append(widget)

    def _visibleWidgets(self) -> list[QtWidgets.QWidget]:
        if self.suitableWidth() <= self.width():
            return self._widgets

        w = self.btn_more.width()
        for index, widget in enumerate(self._widgets):
            w += widget.width()
            if index > 0:
                w += self.spacing()

            if w > self.width():
                break

        return self._widgets[:index]

    def suitableWidth(self) -> int:
        widths = [w.width() for w in self._widgets]
        if self._hidden_actions:
            widths.append(self.btn_more.width())

        return sum(widths) + self.spacing() * max(len(widths) - 1, 0)

    def resizeToSuitableWidth(self) -> None:
        self.setFixedWidth(self.suitableWidth())

    def setFont(self, arg__1: QtGui.QFont | str | Sequence[str]) -> None:
        super().setFont(arg__1)
        for button in self.command_buttons:
            button.setFont(arg__1)

    def _showMoreActionsMenu(self) -> None:
        self.btn_more.clearState()
        actions = self._hidden_actions.copy()

        for w in reversed(self._hidden_widgets):
            if isinstance(w, CommandButton):
                actions.insert(0, w.action())

        menu = QtWidgets.QMenu(self)
        menu.addActions(actions)
        menu.exec(self.btn_more.mapToGlobal(QtCore.QPoint(0, self.btn_more.height())))
