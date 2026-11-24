from itertools import pairwise

from PySide6.QtCore import (
    Property,
    QEvent,
    QObject,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSequentialAnimationGroup,
    Qt,
    Slot,
)
from PySide6.QtGui import QColor, QFont, QHideEvent, QPainter, QPaintEvent, QPen, QShowEvent
from PySide6.QtWidgets import QWidget

from pyside_widgets._utils import ColorLike


class IndeterminateSpinner(QWidget):
    """
    Indeterminate ring spinner, based on `qfluentwidgets.IndeterminateProgressRing`.

    The animation runs only while the spinner is visible, so a hidden spinner costs no timer wake-ups.
    """

    def __init__(self, parent: QWidget | None = None, *, start: bool = True) -> None:
        """
        Args:
            parent: Parent widget.
            start: Whether the spinner spins when it is shown. ``start()`` and ``stop()`` change this later.
        """
        super().__init__(parent)

        self._bg_color = QColor(0, 0, 0, 0)
        self._bar_color = QColor()
        self._stroke_width = 6
        self._start_angle = 0
        self._span_angle = 0
        self._spinning = start

        self.ani_group = QParallelAnimationGroup(self)
        self.ani_group.addAnimation(self._sequence(b"startAngle", 0, 450, 1080))
        self.ani_group.addAnimation(self._sequence(b"spanAngle", 0, 180, 0))
        self.ani_group.setLoopCount(-1)

        self.setFixedSize(80, 80)

    def _sequence(self, property_name: bytes, *values: int) -> QSequentialAnimationGroup:
        """One-second animations of ``property_name`` through consecutive ``values``."""
        group = QSequentialAnimationGroup(self)
        for start, end in pairwise(values):
            animation = QPropertyAnimation(self, property_name, self)
            animation.setDuration(1000)
            animation.setStartValue(start)
            animation.setEndValue(end)
            group.addAnimation(animation)
        return group

    @Slot()
    def start(self) -> None:
        """Spin whenever the spinner is visible."""
        self._spinning = True
        if self.isVisible():
            self._run()

    @Slot()
    def stop(self) -> None:
        """Stop spinning and clear the ring."""
        self._spinning = False
        self._halt()

    def _run(self) -> None:
        self._start_angle = 0
        self._span_angle = 0
        self.ani_group.start()

    def _halt(self) -> None:
        self.ani_group.stop()
        self._start_angle = 0
        self._span_angle = 0
        self.update()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self._spinning:
            self._run()

    def hideEvent(self, event: QHideEvent) -> None:
        super().hideEvent(event)
        self._halt()

    def set_bg_color(self, color: ColorLike) -> None:
        """Set the color of the full ring behind the moving arc. Invalid colors are ignored."""
        bg_color = QColor(color)
        if not bg_color.isValid():
            return
        self._bg_color = bg_color
        self.update()

    def set_bar_color(self, color: ColorLike) -> None:
        """Set the color of the moving arc. Invalid colors are ignored."""
        bar_color = QColor(color)
        if not bar_color.isValid():
            return
        self._bar_color = bar_color
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        stroke = self._stroke_width
        diameter = min(self.height(), self.width()) - stroke
        ring = QRectF(stroke / 2, self.height() / 2 - diameter / 2, diameter, diameter)
        pen = QPen(self._bg_color, stroke, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        with QPainter(self) as painter:
            painter.setRenderHints(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawArc(ring, 0, 360 * 16)

            pen.setColor(self._bar_color)
            painter.setPen(pen)
            start_angle = -self._start_angle + 180
            painter.drawArc(ring, (start_angle % 360) * 16, -self._span_angle * 16)

    def get_stroke_width(self) -> int:
        return self._stroke_width

    def set_stroke_width(self, width: int) -> None:
        self._stroke_width = width
        self.update()

    def get_start_angle(self) -> int:
        return self._start_angle

    def set_start_angle(self, angle: int) -> None:
        self._start_angle = angle
        self.update()

    def get_span_angle(self) -> int:
        return self._span_angle

    def set_span_angle(self, angle: int) -> None:
        self._span_angle = angle
        self.update()

    strokeWidth = Property(int, get_stroke_width, set_stroke_width)
    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setStrokeWidth = set_stroke_width
    # Animation targets of ani_group, not settings.
    startAngle = Property(int, get_start_angle, set_start_angle, designable=False)
    spanAngle = Property(int, get_span_angle, set_span_angle, designable=False)


class OverlayWidget(QWidget):
    """
    Semi-transparent overlay with a spinner and a message that covers and disables its parent while shown.

    ``show()``, ``setVisible(True)`` and ``show_overlay()`` are equivalent. Hiding the overlay gives the parent back
    the enabled state it had when the overlay was shown. The overlay follows the parent's size while visible.
    """

    _TEXT_SPACING = 12

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._target = parent
        self._target_was_enabled = True
        self._covering = False
        self._text = ""
        self._bg_color = QColor(0, 0, 0, 128)
        self._bar_color = QColor("cornflowerblue")

        self._text_font = QFont(self.font())
        self._text_font.setPointSize(28)
        self._text_font.setWeight(QFont.Weight.DemiBold)

        self._spinner = IndeterminateSpinner(self)
        self._spinner.set_bar_color(self._bar_color)

        self.hide()
        self._target.installEventFilter(self)

    def setVisible(self, visible: bool) -> None:
        # Overridden rather than showEvent/hideEvent: those also fire when the parent window is shown or hidden, and
        # they do not fire at all while the parent is not on screen yet.
        if visible != self._covering:
            self._covering = visible
            if visible:
                self._target_was_enabled = self._target.isEnabled()
                self._target.setEnabled(False)
                self._fit_to_target()
                self.raise_()
            else:
                self._target.setEnabled(self._target_was_enabled)
        super().setVisible(visible)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._target and event.type() == QEvent.Type.Resize and self._covering:
            self._fit_to_target()
        return super().eventFilter(watched, event)

    def _fit_to_target(self) -> None:
        self.setGeometry(self._target.rect())
        spinner = self._spinner
        spinner.move((self.width() - spinner.width()) // 2, (self.height() - spinner.height()) // 2)

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self) as painter:
            painter.fillRect(self.rect(), self._bg_color)
            if not self._text:
                return
            # Drawn here instead of in a QLabel: the overlay is disabled together with its parent, and a disabled
            # label is rendered greyed or etched depending on the style.
            painter.setFont(self._text_font)
            painter.setPen(Qt.GlobalColor.white)
            above_spinner = QRect(0, 0, self.width(), max(0, self._spinner.y() - self._TEXT_SPACING))
            flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom | Qt.TextFlag.TextWordWrap
            painter.drawText(above_spinner, flags, self._text)

    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color: ColorLike) -> None:
        """Set the (usually translucent) color drawn over the parent widget."""
        self._bg_color = QColor(color)
        self.update()

    def get_text(self) -> str:
        return self._text

    @Slot(str)
    def set_text(self, text: str) -> None:
        """Set the message drawn above the spinner."""
        self._text = text
        self.update()

    def get_bar_color(self) -> QColor:
        return self._bar_color

    def set_bar_color(self, color: ColorLike) -> None:
        """Set the color of the spinner ring."""
        self._bar_color = QColor(color)
        self._spinner.set_bar_color(self._bar_color)

    def show_overlay(self, text: str | None = None) -> None:
        """Disable the parent widget, optionally update the message, and show the overlay on top of it."""
        if text is not None:
            self.set_text(text)
        self.show()

    @Slot()
    def hide_overlay(self) -> None:
        """Hide the overlay and restore the parent's enabled state."""
        self.hide()

    @Slot(bool)
    def toggle_overlay(self, visible: bool) -> None:
        self.setVisible(visible)

    text = Property(str, get_text, set_text)
    bgColor = Property(QColor, get_bg_color, set_bg_color)
    barColor = Property(QColor, get_bar_color, set_bar_color)

    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setText = set_text
    setBgColor = set_bg_color
    setBarColor = set_bar_color
