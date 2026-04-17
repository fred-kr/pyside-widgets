from PySide6.QtCore import (
    Property,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRectF,
    QSequentialAnimationGroup,
    Qt,
    Slot,
)
from PySide6.QtDesigner import QDesignerCustomWidgetInterface, QDesignerFormEditorInterface
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

type ColorLike = Qt.GlobalColor | QColor | str


class IndeterminateSpinner(QProgressBar):
    """
    Indeterminate spinner, based on `qfluentwidgets.IndeterminateProgressRing`.
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

        # Initialize start angle animation
        self.start_angle_ani1.setDuration(1000)
        self.start_angle_ani1.setStartValue(0)
        self.start_angle_ani1.setEndValue(450)

        self.start_angle_ani2.setDuration(1000)
        self.start_angle_ani2.setStartValue(450)
        self.start_angle_ani2.setEndValue(1080)

        self.start_angle_ani_group.addAnimation(self.start_angle_ani1)
        self.start_angle_ani_group.addAnimation(self.start_angle_ani2)

        # Initialize span angle animation
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

    def set_bg_color(self, color: QColor | str) -> None:
        bg_color = QColor(color)
        if not bg_color.isValid():
            return
        self._bg_color = bg_color
        self.update()

    def set_bar_color(self, color: QColor | str) -> None:
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

        # Draw background
        bc = self._bg_color
        pen = QPen(
            bc,
            cw,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

        # Draw bar
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
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.hide()
        self._target = parent

        self._bg_color = QColor(0, 0, 0, 128)
        self._bar_color = QColor("cornflowerblue")

        self._container = QWidget(self)
        self._container.setStyleSheet("background: rgba(0, 0, 0, 128);")

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

        self._layout_content.addWidget(
            self._text,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        )
        self._layout_content.addWidget(
            self._spinner,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )

        self._layout.addWidget(
            self._content,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )

    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color: ColorLike) -> None:
        """
        Set the background color of the container widget to the provided rgba values.

        Args:
            color (ColorLike): The color to set the background to
        """
        self._bg_color = QColor(color)
        r, g, b, a = self._bg_color.red(), self._bg_color.green(), self._bg_color.blue(), self._bg_color.alpha()
        self._container.setStyleSheet(f"background: rgba({r}, {g}, {b}, {a});")

    def get_text(self) -> str:
        return self._text.text()

    def set_text(self, text: str) -> None:
        """
        Set the text of the label

        Args:
            text (str): The text to display
        """
        self._text.setText(text)

    def get_bar_color(self) -> QColor:
        return self._bar_color

    def set_bar_color(self, color: ColorLike) -> None:
        """Set the color of the spinner"""
        self._bar_color = QColor(color)
        self._spinner.set_bar_color(self._bar_color)

    def show_overlay(self, text: str | None = None) -> None:
        """
        Disables the target widget, updates the label text if provided, and shows the overlay

        Args:
            text: The text to display, defaults to None
        """
        self._target.setEnabled(False)

        if text is not None:
            self._text.setText(text)

        self.setGeometry(self._target.geometry())
        self._container.move(0, 0)
        self._container.resize(self._target.size())
        self.move(0, 0)
        self.raise_()
        self.show()

    def hide_overlay(self) -> None:
        """
        Enables the target widget and hides the overlay
        """
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


class OverlayWidgetPlugin(QDesignerCustomWidgetInterface):
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    def createWidget(self, parent: QWidget) -> OverlayWidget:
        return OverlayWidget(parent=parent)

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='OverlayWidget' name='overlayWidget'>
                <property name='text'>
                    <string>Running...</string>
                </property>
                <property name='bg_color'>
                    <color alpha='128'>
                        <red>0</red>
                        <green>0</green>
                        <blue>0</blue>
                    </color>
                </property>
                <property name='bar_color'>
                    <color alpha='255'>
                        <red>100</red>
                        <green>149</green>
                        <blue>237</blue>
                    </color>
                </property>
            </widget>
        </ui>
        """

    def group(self) -> str:
        return ""

    def icon(self) -> QIcon:
        return QIcon()

    def includeFile(self) -> str:
        return __name__

    def initialize(self, core: QDesignerFormEditorInterface) -> None:
        if self._initialized:
            return

        self._initialized = True

    def isContainer(self) -> bool:
        return False

    def isInitialized(self) -> bool:
        return self._initialized

    def name(self) -> str:
        return "OverlayWidget"

    def toolTip(self) -> str:
        return "Can be used to lock the UI while an operation is running"

    def whatsThis(self) -> str:
        return self.toolTip()
