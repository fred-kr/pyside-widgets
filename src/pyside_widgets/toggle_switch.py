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
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QCheckBox, QSizePolicy, QWidget

type ColorLike = Qt.GlobalColor | QColor | str


class ToggleSwitch(QCheckBox):
    """QCheckBox drawn as a sliding toggle switch."""

    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_gray_pen = QPen(Qt.GlobalColor.lightGray)

    def __init__(
        self,
        parent: QWidget | None = None,
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

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        cont_rect = self.contentsRect()
        handle_radius = round(0.24 * cont_rect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(self._transparent_pen)

        bar_rect = QRectF(0, 0, cont_rect.width() - handle_radius, 0.40 * cont_rect.height())
        bar_rect.moveCenter(cont_rect.center().toPointF())
        rounding = bar_rect.height() / 2

        trail_length = cont_rect.width() - 2 * handle_radius
        x_pos = cont_rect.x() + handle_radius + trail_length * self._handle_position
        handle_center = QPointF(x_pos, bar_rect.center().y())

        self._paint_pulse(p, handle_center)

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(bar_rect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(bar_rect, rounding, rounding)
            p.setPen(self._light_gray_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(handle_center, handle_radius, handle_radius)
        p.end()

    def _paint_pulse(self, painter: QPainter, center: QPointF) -> None:
        """Hook for subclasses to draw behind the handle. The plain switch draws nothing."""

    @Slot(bool)
    def _on_toggled(self, checked: bool) -> None:
        self._handle_position = 1.0 if checked else 0.0
        self.update()

    def get_handle_position(self) -> float:
        return self._handle_position

    def set_handle_position(self, pos: float) -> None:
        self._handle_position = pos
        self.update()

    def get_pulse_radius(self) -> float:
        return self._pulse_radius

    def set_pulse_radius(self, radius: float) -> None:
        self._pulse_radius = radius
        self.update()

    handle_position = Property(float, get_handle_position, set_handle_position)
    pulse_radius = Property(float, get_pulse_radius, set_pulse_radius)


class AnimatedToggleSwitch(ToggleSwitch):
    """``ToggleSwitch`` whose handle slides and pulses when toggled."""

    def __init__(
        self,
        parent: QWidget | None = None,
        bar_color: ColorLike = Qt.GlobalColor.gray,
        checked_color: ColorLike = "#00B0FF",
        handle_color: ColorLike = Qt.GlobalColor.white,
        pulse_unchecked_color: ColorLike = "#44999999",
        pulse_checked_color: ColorLike = "#4400B0EE",
    ) -> None:
        super().__init__(parent, bar_color, checked_color, handle_color)

        self._pulse_unchecked_brush = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_brush = QBrush(QColor(pulse_checked_color))

        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(200)

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
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
