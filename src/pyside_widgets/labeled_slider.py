import enum
import warnings
from typing import ClassVar

from PySide6 import QtCore, QtGui, QtWidgets


class ValueSlider(QtWidgets.QSlider):
    """Horizontal QSlider that paints its current value above the handle."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

    def setTickPosition(self, position: QtWidgets.QSlider.TickPosition) -> None:
        super().setTickPosition(position)
        self.updateGeometry()

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        super().paintEvent(ev)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(self.palette().color(QtGui.QPalette.ColorRole.WindowText))

        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)

        handle_rect = self.style().subControlRect(
            QtWidgets.QStyle.ComplexControl.CC_Slider, opt, QtWidgets.QStyle.SubControl.SC_SliderHandle, self
        )
        slider_thickness = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SliderThickness, opt, self)
        handle_top = handle_rect.center().y() - slider_thickness // 2 + 1

        value_text = str(self.value())
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(value_text)
        text_height = metrics.height()

        # Keep the text inside the widget at both ends.
        text_left = max(handle_rect.center().x() - text_width // 2, 0)
        text_left = min(text_left, self.width() - text_width)
        text_rect = QtCore.QRect(text_left, handle_top - text_height, text_width, text_height)

        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, value_text)

    def minimumSizeHint(self) -> QtCore.QSize:
        tick_pos = self.tickPosition()
        if tick_pos == QtWidgets.QSlider.TickPosition.NoTicks:
            return QtCore.QSize(0, 50)
        if tick_pos in (QtWidgets.QSlider.TickPosition.TicksBelow, QtWidgets.QSlider.TickPosition.TicksAbove):
            return QtCore.QSize(0, 75)
        if tick_pos == QtWidgets.QSlider.TickPosition.TicksBothSides:
            return QtCore.QSize(0, 100)
        return super().minimumSizeHint()


class LabeledSlider(QtWidgets.QWidget):
    """
    ``ValueSlider`` with a title label and minimum/maximum labels.

    Range and value are mirrored here because they affect the labels. Everything else (ticks, steps, tracking, ...) is
    reached through the ``slider`` attribute.
    """

    actionTriggered: ClassVar = QtCore.Signal(int)
    rangeChanged: ClassVar = QtCore.Signal(int, int)
    sliderMoved: ClassVar = QtCore.Signal(int)
    sliderPressed: ClassVar = QtCore.Signal()
    sliderReleased: ClassVar = QtCore.Signal()
    valueChanged: ClassVar = QtCore.Signal(int)

    class TitleLabelPosition(enum.Enum):
        TOP_LEFT = QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        TOP_CENTER = QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter
        TOP_RIGHT = QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        BOTTOM_LEFT = QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft
        BOTTOM_CENTER = QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter
        BOTTOM_RIGHT = QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight
        LEFT = QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft
        RIGHT = QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignRight

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        title: str = "",
        title_pos: TitleLabelPosition = TitleLabelPosition.TOP_LEFT,
        show_min_max: bool = True,
    ) -> None:
        super().__init__(parent)

        self.slider = ValueSlider(self)
        self.slider.actionTriggered.connect(self.actionTriggered.emit)
        self.slider.rangeChanged.connect(self._on_range_changed)
        self.slider.sliderMoved.connect(self.sliderMoved.emit)
        self.slider.sliderPressed.connect(self.sliderPressed.emit)
        self.slider.sliderReleased.connect(self.sliderReleased.emit)
        self.slider.valueChanged.connect(self.valueChanged.emit)

        self.title_label = QtWidgets.QLabel(title, self)
        self.title_label.setVisible(bool(title))

        self.minimum_label = QtWidgets.QLabel(str(self.slider.minimum()), self)
        self.maximum_label = QtWidgets.QLabel(str(self.slider.maximum()), self)
        self.minimum_label.setVisible(show_min_max)
        self.maximum_label.setVisible(show_min_max)

        tlp = self.TitleLabelPosition
        alignment = title_pos.value
        align_right = QtCore.Qt.AlignmentFlag.AlignRight
        align_left = QtCore.Qt.AlignmentFlag.AlignLeft

        if title_pos in (tlp.LEFT, tlp.RIGHT):
            h_layout = QtWidgets.QHBoxLayout(self)
            if title_pos is tlp.LEFT:
                h_layout.addWidget(self.title_label, 0, alignment)
                h_layout.addSpacing(16)
            h_layout.addWidget(self.minimum_label, 0, align_right)
            h_layout.addWidget(self.slider, 1)
            h_layout.addWidget(self.maximum_label, 0, align_left)
            if title_pos is tlp.RIGHT:
                h_layout.addSpacing(16)
                h_layout.addWidget(self.title_label, 0, alignment)
        else:
            grid = QtWidgets.QGridLayout(self)
            grid.setVerticalSpacing(0)
            title_on_top = title_pos in (tlp.TOP_LEFT, tlp.TOP_CENTER, tlp.TOP_RIGHT)
            title_row, slider_row = (0, 1) if title_on_top else (1, 0)
            grid.addWidget(self.title_label, title_row, 1, alignment)
            grid.addWidget(self.minimum_label, slider_row, 0, align_right)
            grid.addWidget(self.slider, slider_row, 1)
            grid.addWidget(self.maximum_label, slider_row, 2, align_left)

    @QtCore.Slot(int, int)
    def _on_range_changed(self, minimum: int, maximum: int) -> None:
        self.minimum_label.setText(str(minimum))
        self.maximum_label.setText(str(maximum))
        self.rangeChanged.emit(minimum, maximum)

    def minimum(self) -> int:
        return self.slider.minimum()

    def setMinimum(self, value: int) -> None:
        self.slider.setMinimum(value)

    def maximum(self) -> int:
        return self.slider.maximum()

    def setMaximum(self, value: int) -> None:
        self.slider.setMaximum(value)

    def setRange(self, min: int, max: int) -> None:
        self.slider.setRange(min, max)

    def value(self) -> int:
        return self.slider.value()

    def setValue(self, value: int) -> None:
        self.slider.setValue(value)

    def orientation(self) -> QtCore.Qt.Orientation:
        return QtCore.Qt.Orientation.Horizontal

    def setOrientation(self, orientation: QtCore.Qt.Orientation) -> None:
        if orientation != QtCore.Qt.Orientation.Horizontal:
            warnings.warn("LabeledSlider only supports horizontal orientation.", stacklevel=2)
