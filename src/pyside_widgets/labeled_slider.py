import enum

from PySide6.QtCore import Property, QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QPainter, QPaintEvent, QPalette
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QWidget,
)


class ValueSlider(QSlider):
    """Horizontal QSlider that paints its current value above the handle."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def paintEvent(self, ev: QPaintEvent) -> None:
        super().paintEvent(ev)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        handle_rect = style.subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self
        )
        slider_thickness = style.pixelMetric(QStyle.PixelMetric.PM_SliderThickness, opt, self)
        handle_top = handle_rect.center().y() - slider_thickness // 2 + 1

        value_text = str(self.value())
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(value_text)
        text_height = metrics.height()

        # Keep the text inside the widget at both ends.
        text_left = max(handle_rect.center().x() - text_width // 2, 0)
        text_left = min(text_left, self.width() - text_width)
        text_rect = QRect(text_left, handle_top - text_height, text_width, text_height)

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, value_text)

    def sizeHint(self) -> QSize:
        # The groove stays vertically centered, so one line of text above the handle costs two lines of height.
        # QSlider.minimumSizeHint() is derived from this method and needs no override of its own.
        hint = super().sizeHint()
        return QSize(hint.width(), hint.height() + 2 * self.fontMetrics().height())


class LabeledSlider(QWidget):
    """
    ``ValueSlider`` with a title label and minimum/maximum labels.

    Range and value are mirrored here because they affect the labels. Everything else (ticks, steps, tracking, ...) is
    reached through the ``slider`` attribute. The slider is always horizontal.
    """

    actionTriggered = Signal(int)
    rangeChanged = Signal(int, int)
    sliderMoved = Signal(int)
    sliderPressed = Signal()
    sliderReleased = Signal()
    valueChanged = Signal(int)

    class TitleLabelPosition(enum.Enum):
        TOP_LEFT = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        TOP_CENTER = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        TOP_RIGHT = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        BOTTOM_LEFT = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft
        BOTTOM_CENTER = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        BOTTOM_RIGHT = Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        LEFT = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        RIGHT = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "",
        title_pos: TitleLabelPosition = TitleLabelPosition.TOP_LEFT,
        show_min_max: bool = True,
    ) -> None:
        super().__init__(parent)

        self.slider = ValueSlider(self)
        self.slider.actionTriggered.connect(self.actionTriggered)
        self.slider.rangeChanged.connect(self._on_range_changed)
        self.slider.sliderMoved.connect(self.sliderMoved)
        self.slider.sliderPressed.connect(self.sliderPressed)
        self.slider.sliderReleased.connect(self.sliderReleased)
        self.slider.valueChanged.connect(self.valueChanged)

        self.title_label = QLabel(title, self)
        self.title_label.setVisible(bool(title))

        self.minimum_label = QLabel(str(self.slider.minimum()), self)
        self.maximum_label = QLabel(str(self.slider.maximum()), self)
        self.minimum_label.setVisible(show_min_max)
        self.maximum_label.setVisible(show_min_max)

        tlp = self.TitleLabelPosition
        alignment = title_pos.value
        align_right = Qt.AlignmentFlag.AlignRight
        align_left = Qt.AlignmentFlag.AlignLeft

        if title_pos in (tlp.LEFT, tlp.RIGHT):
            h_layout = QHBoxLayout(self)
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
            grid = QGridLayout(self)
            grid.setVerticalSpacing(0)
            title_on_top = title_pos in (tlp.TOP_LEFT, tlp.TOP_CENTER, tlp.TOP_RIGHT)
            title_row, slider_row = (0, 1) if title_on_top else (1, 0)
            grid.addWidget(self.title_label, title_row, 1, alignment)
            grid.addWidget(self.minimum_label, slider_row, 0, align_right)
            grid.addWidget(self.slider, slider_row, 1)
            grid.addWidget(self.maximum_label, slider_row, 2, align_left)

    @Slot(int, int)
    def _on_range_changed(self, minimum: int, maximum: int) -> None:
        self.minimum_label.setText(str(minimum))
        self.maximum_label.setText(str(maximum))
        self.rangeChanged.emit(minimum, maximum)

    def get_title(self) -> str:
        return self.title_label.text()

    @Slot(str)
    def set_title(self, title: str) -> None:
        """Set the title text. An empty title hides the title label."""
        self.title_label.setText(title)
        self.title_label.setVisible(bool(title))

    def minimum(self) -> int:
        return self.slider.minimum()

    @Slot(int)
    def setMinimum(self, value: int) -> None:
        self.slider.setMinimum(value)

    def maximum(self) -> int:
        return self.slider.maximum()

    @Slot(int)
    def setMaximum(self, value: int) -> None:
        self.slider.setMaximum(value)

    @Slot(int, int)
    def setRange(self, min: int, max: int) -> None:
        self.slider.setRange(min, max)

    def value(self) -> int:
        return self.slider.value()

    @Slot(int)
    def setValue(self, value: int) -> None:
        self.slider.setValue(value)

    # Qt properties. "sliderValue" rather than "value" because a Property occupies the class attribute of its own
    # name and would replace the value() method that mirrors QSlider.
    title = Property(str, get_title, set_title)
    sliderValue = Property(int, value, setValue, notify=valueChanged, user=True)

    # pyside6-uic writes a Designer property as a call to set<PropertyName>().
    setTitle = set_title
    setSliderValue = setValue
