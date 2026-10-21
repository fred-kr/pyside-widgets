from PySide6.QtCore import (
    Property,
    QEvent,
    QObject,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRectF,
    QSequentialAnimationGroup,
    Qt,
    Slot,
)
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

type ColorLike = Qt.GlobalColor | QColor | str


class IndeterminateSpinner(QProgressBar):
    """
    Indeterminate ring spinner, based on `qfluentwidgets.IndeterminateProgressRing`.
    """

    def __init__(self, parent: QWidget | None = None, start: bool = True) -> None:
        super().__init__(parent)

        self._bg_color = QColor(0, 0, 0, 0)
        self._bar_color = QColor()
        self._stroke_width = 6

        self._startAngle = -180
        self._spanAngle = 0

        self.start_angle_ani1 = QPropertyAnimation(self, b"startAngle", self)
        self.start_angle_ani2 = QPropertyAnimation(self, b"startAngle", self)
        self.span_angle_ani1 = QPropertyAnimation(self, b"spanAngle", self)
        self.span_angle_ani2 = QPropertyAnimation(self, b"spanAngle", self)

        self.start_angle_ani_group = QSequentialAnimationGroup(self)
        self.span_angle_ani_group = QSequentialAnimationGroup(self)
        self.ani_group = QParallelAnimationGroup(self)

        self.start_angle_ani1.setDuration(1000)
        self.start_angle_ani1.setStartValue(0)
        self.start_angle_ani1.setEndValue(450)

        self.start_angle_ani2.setDuration(1000)
        self.start_angle_ani2.setStartValue(450)
        self.start_angle_ani2.setEndValue(1080)

        self.start_angle_ani_group.addAnimation(self.start_angle_ani1)
        self.start_angle_ani_group.addAnimation(self.start_angle_ani2)

        self.span_angle_ani1.setDuration(1000)
        self.span_angle_ani1.setStartValue(0)
        self.span_angle_ani1.setEndValue(180)

        self.span_angle_ani2.setDuration(1000)
        self.span_angle_ani2.setStartValue(180)
        self.span_angle_ani2.setEndValue(0)

        self.span_angle_ani_group.addAnimation(self.span_angle_ani1)
        self.span_angle_ani_group.addAnimation(self.span_angle_ani2)

        self.ani_group.addAnimation(self.start_angle_ani_group)
        self.ani_group.addAnimation(self.span_angle_ani_group)
        self.ani_group.setLoopCount(-1)

        self.setFixedSize(80, 80)

        if start:
            self.start()

    def start(self) -> None:
        self._startAngle = 0
        self._spanAngle = 0
        self.ani_group.start()

    def stop(self) -> None:
        self.ani_group.stop()
        self._startAngle = 0
        self._spanAngle = 0

    def set_bg_color(self, color: ColorLike) -> None:
        bg_color = QColor(color)
        if not bg_color.isValid():
            return
        self._bg_color = bg_color
        self.update()

    def set_bar_color(self, color: ColorLike) -> None:
        bar_color = QColor(color)
        if not bar_color.isValid():
            return
        self._bar_color = bar_color
        self.update()

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cw = self._stroke_width
        w = min(self.height(), self.width()) - cw
        rc = QRectF(cw / 2, self.height() / 2 - w / 2, w, w)

        pen = QPen(self._bg_color, cw, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

        pen.setColor(self._bar_color)
        painter.setPen(pen)
        start_angle = -self._startAngle + 180
        painter.drawArc(rc, (start_angle % 360) * 16, -self._spanAngle * 16)

    def get_stroke_width(self) -> int:
        return self._stroke_width

    def set_stroke_width(self, width: int) -> None:
        self._stroke_width = width
        self.update()

    def get_start_angle(self) -> int:
        return self._startAngle

    def set_start_angle(self, angle: int) -> None:
        self._startAngle = angle
        self.update()

    def get_span_angle(self) -> int:
        return self._spanAngle

    def set_span_angle(self, angle: int) -> None:
        self._spanAngle = angle
        self.update()

    stroke_width = Property(int, get_stroke_width, set_stroke_width)
    startAngle = Property(int, get_start_angle, set_start_angle)
    spanAngle = Property(int, get_span_angle, set_span_angle)


class OverlayWidget(QWidget):
    """
    Semi-transparent overlay with a spinner and a message that covers and disables its parent while shown.

    The overlay follows the parent's size while visible.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.hide()
        self._target = parent
        self._target.installEventFilter(self)

        self._bg_color = QColor(0, 0, 0, 128)
        self._bar_color = QColor("cornflowerblue")

        self._container = QWidget(self)

        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._content = QWidget(self._container)
        self._content.setStyleSheet("background: rgba(0, 0, 0, 0);")

        self._layout_content = QVBoxLayout(self._content)
        self._layout_content.setSpacing(12)

        font = QApplication.font()
        font.setPointSize(28)
        font.setWeight(QFont.Weight.DemiBold)

        self._text = QLabel(self._content)
        self._text.setFont(font)
        self._text.setStyleSheet("background: transparent; color: white;")
        self._text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = IndeterminateSpinner(self._content)
        self._spinner.set_bar_color(self._bar_color)

        self._layout_content.addWidget(self._text, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._layout_content.addWidget(self._spinner, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(self._content, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.set_bg_color(self._bg_color)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._target and event.type() == QEvent.Type.Resize and self.isVisible():
            self._fit_to_target()
        return super().eventFilter(watched, event)

    def _fit_to_target(self) -> None:
        self.setGeometry(self._target.rect())
        self._container.setGeometry(self.rect())

    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color: ColorLike) -> None:
        """Set the (usually translucent) color drawn over the parent widget."""
        self._bg_color = QColor(color)
        r, g, b, a = self._bg_color.red(), self._bg_color.green(), self._bg_color.blue(), self._bg_color.alpha()
        self._container.setStyleSheet(f"background: rgba({r}, {g}, {b}, {a});")

    def get_text(self) -> str:
        return self._text.text()

    def set_text(self, text: str) -> None:
        self._text.setText(text)

    def get_bar_color(self) -> QColor:
        return self._bar_color

    def set_bar_color(self, color: ColorLike) -> None:
        """Set the color of the spinner ring."""
        self._bar_color = QColor(color)
        self._spinner.set_bar_color(self._bar_color)

    def show_overlay(self, text: str | None = None) -> None:
        """Disable the parent widget, optionally update the message, and show the overlay on top of it."""
        self._target.setEnabled(False)
        if text is not None:
            self._text.setText(text)
        self._fit_to_target()
        self.raise_()
        self.show()

    def hide_overlay(self) -> None:
        """Hide the overlay and re-enable the parent widget."""
        self._target.setEnabled(True)
        self.hide()

    @Slot(bool)
    def toggle_overlay(self, visible: bool) -> None:
        if visible:
            self.show_overlay()
        else:
            self.hide_overlay()

    text = Property(str, get_text, set_text)
    bg_color = Property(QColor, get_bg_color, set_bg_color)
    bar_color = Property(QColor, get_bar_color, set_bar_color)
