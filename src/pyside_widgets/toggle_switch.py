from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSequentialAnimationGroup,
    QSize,
    Qt,
    Slot,
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QCheckBox, QSizePolicy, QStyle, QStyleOptionFocusRect, QWidget

from pyside_widgets._utils import ColorLike

_DISABLED_OPACITY = 0.4


class ToggleSwitch(QCheckBox):
    """
    QCheckBox drawn as a sliding toggle switch.

    Known limitation: the switch draws no label. ``setText()`` is accepted and ignored; put a ``QLabel`` next to it.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        bar_color: ColorLike = Qt.GlobalColor.gray,
        checked_color: ColorLike = "#00B0FF",
        handle_color: ColorLike = Qt.GlobalColor.white,
    ) -> None:
        super().__init__(parent)

        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        self._handle_position = 0.0
        self._pulse_radius = 0.0

        self.setContentsMargins(8, 0, 8, 0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.toggled.connect(self._on_toggled)

    def sizeHint(self) -> QSize:
        return QSize(58, 45)

    def hitButton(self, pos: QPoint) -> bool:
        return self.contentsRect().contains(pos)

    def paintEvent(self, event: QPaintEvent) -> None:
        cont_rect = self.contentsRect()
        handle_radius = round(0.24 * cont_rect.height())

        bar_rect = QRectF(0, 0, cont_rect.width() - handle_radius, 0.40 * cont_rect.height())
        bar_rect.moveCenter(cont_rect.center().toPointF())
        rounding = bar_rect.height() / 2

        trail_length = cont_rect.width() - 2 * handle_radius
        x_pos = cont_rect.x() + handle_radius + trail_length * self._handle_position
        handle_center = QPointF(x_pos, bar_rect.center().y())

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            if not self.isEnabled():
                painter.setOpacity(_DISABLED_OPACITY)

            self._paint_pulse(painter, handle_center)

            if self.isChecked():
                painter.setBrush(self._bar_checked_brush)
                painter.drawRoundedRect(bar_rect, rounding, rounding)
                painter.setBrush(self._handle_checked_brush)
            else:
                painter.setBrush(self._bar_brush)
                painter.drawRoundedRect(bar_rect, rounding, rounding)
                painter.setPen(Qt.GlobalColor.lightGray)
                painter.setBrush(self._handle_brush)
            painter.drawEllipse(handle_center, handle_radius, handle_radius)

            if self.hasFocus():
                # The style decides whether to draw it; most show the frame for keyboard focus only.
                focus = QStyleOptionFocusRect()
                focus.initFrom(self)
                focus.rect = cont_rect
                painter.setOpacity(1.0)
                self.style().drawPrimitive(QStyle.PrimitiveElement.PE_FrameFocusRect, focus, painter, self)

    def _paint_pulse(self, painter: QPainter, center: QPointF) -> None:
        """Hook for subclasses to draw behind the handle. The plain switch draws nothing."""

    @Slot(bool)
    def _on_toggled(self, checked: bool) -> None:
        self._handle_position = 1.0 if checked else 0.0
        self.update()

    def get_handle_position(self) -> float:
        """Position of the handle along the bar, from 0.0 (unchecked side) to 1.0 (checked side)."""
        return self._handle_position

    def set_handle_position(self, pos: float) -> None:
        self._handle_position = pos
        self.update()

    def get_pulse_radius(self) -> float:
        return self._pulse_radius

    def set_pulse_radius(self, radius: float) -> None:
        self._pulse_radius = radius
        self.update()

    # Animation targets, not settings.
    handlePosition = Property(float, get_handle_position, set_handle_position, designable=False)
    pulseRadius = Property(float, get_pulse_radius, set_pulse_radius, designable=False)


class AnimatedToggleSwitch(ToggleSwitch):
    """``ToggleSwitch`` whose handle slides and pulses when toggled."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        bar_color: ColorLike = Qt.GlobalColor.gray,
        checked_color: ColorLike = "#00B0FF",
        handle_color: ColorLike = Qt.GlobalColor.white,
        pulse_unchecked_color: ColorLike = "#44999999",
        pulse_checked_color: ColorLike = "#4400B0EE",
    ) -> None:
        super().__init__(parent, bar_color=bar_color, checked_color=checked_color, handle_color=handle_color)

        self._pulse_unchecked_brush = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_brush = QBrush(QColor(pulse_checked_color))

        self.animation = QPropertyAnimation(self, b"handlePosition", self)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(200)

        self.pulse_anim = QPropertyAnimation(self, b"pulseRadius", self)
        self.pulse_anim.setDuration(350)
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup(self)
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.pulse_anim)

    def _paint_pulse(self, painter: QPainter, center: QPointF) -> None:
        if self.pulse_anim.state() != QPropertyAnimation.State.Running:
            return
        painter.setBrush(self._pulse_checked_brush if self.isChecked() else self._pulse_unchecked_brush)
        painter.drawEllipse(center, self._pulse_radius, self._pulse_radius)

    @Slot(bool)
    def _on_toggled(self, checked: bool) -> None:
        self.animations_group.stop()
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animations_group.start()
