"""Tabbed demo of every widget in the package. Run with ``uv run demo``."""

import enum
import sys
import types
from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

from pyside_widgets import (
    AnimatedToggleSwitch,
    ColorPickerButton,
    CommandBar,
    DataTreeWidget,
    DecimalSpinBox,
    EnumComboBox,
    GroupedComboBox,
    LabeledSlider,
    OverlayWidget,
    ResizableMessageBox,
    SearchableDataTreeWidget,
    SettingCard,
    ToggleSwitch,
)
from pyside_widgets._icons import get_icon


class EnumA(enum.Enum):
    A = 1
    B = 2
    C = 3


class SettingEnum(enum.Enum):
    DEFAULT = enum.auto()
    SETTING_A = enum.auto()
    SETTING_B = enum.auto()
    SETTING_C = enum.auto()


def _make_traceback() -> types.TracebackType | None:
    try:
        raise ValueError("Some error")
    except ValueError:
        return sys.exc_info()[2]


def _make_exception() -> ZeroDivisionError:
    try:
        raise ZeroDivisionError("division by zero")
    except ZeroDivisionError as exc:
        return exc


def _example_data() -> dict[str, Any]:
    data: dict[str, Any] = {
        "a list": [1, 2, 3, 4, 5, 6, {"nested1": "aaaaa", "nested2": "bbbbb"}, "seven"],
        "a dict": {"x": 1, "y": 2, "z": "three"},
        "a long string": "lorem ipsum " * 20,
        "a traceback": _make_traceback(),
        "a function": _make_traceback,
        "a class": DataTreeWidget,
    }
    try:
        import numpy as np
    except ImportError:
        return data
    rng = np.random.default_rng(0)
    data["a small array"] = rng.integers(10, size=(40, 10))
    data["a large array"] = rng.normal(size=100_000)
    return data


def _vbox_tab(*widgets: QtWidgets.QWidget, stretch_last: bool = False) -> QtWidgets.QWidget:
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    for i, widget in enumerate(widgets):
        is_last = i == len(widgets) - 1
        layout.addWidget(widget, 1 if (stretch_last and is_last) else 0)
    if not stretch_last:
        layout.addStretch()
    return container


def main() -> None:
    QtWidgets.QApplication.setStyle("Fusion")
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Widget Gallery")
    tabs = QtWidgets.QTabWidget()

    # GroupedComboBox
    grouped_combo_box = GroupedComboBox()
    grouped_combo_box.add_parent_item("Group 1")
    grouped_combo_box.add_child_item("Item 1", EnumA.A)
    grouped_combo_box.add_child_item("Item 2", EnumA.B)
    grouped_combo_box.add_child_item("Item 3", EnumA.C)
    grouped_combo_box.add_separator()
    grouped_combo_box.add_parent_item("Group 2")
    grouped_combo_box.add_child_item("Item 4", EnumA.A.value)
    grouped_combo_box.add_child_item("Item 5", EnumA.B.value)
    grouped_combo_box.add_child_item("Item 6", EnumA.C.value)
    grouped_combo_box.setCurrentIndex(1)
    grouped_combo_box.currentIndexChanged.connect(
        lambda: print(f"Selected item: {grouped_combo_box.currentText()}, item data: {grouped_combo_box.currentData()}")
    )
    tabs.addTab(_vbox_tab(grouped_combo_box), "GroupedComboBox")

    # JupyterConsoleWindow (optional dependency)
    try:
        from pyside_widgets import JupyterConsoleWindow
    except ImportError:
        tabs.addTab(_vbox_tab(QtWidgets.QLabel("Install the 'jupyter' extra to see the console.")), "Jupyter")
    else:
        jupyter_console = JupyterConsoleWindow(style="lightbg", namespace={"app": app, "window": window})
        jupyter_console.console.execute("print('Hello from Jupyter Console!')", True)
        tabs.addTab(jupyter_console, "JupyterConsoleWindow")

    # OverlayWidget
    base_widget = QtWidgets.QTextEdit("This is the base widget")
    overlay_widget = OverlayWidget(parent=base_widget)
    overlay_button = QtWidgets.QPushButton("Toggle Overlay")
    overlay_button.clicked.connect(lambda: overlay_widget.toggle_overlay(not overlay_widget.isVisible()))
    tabs.addTab(_vbox_tab(overlay_button, base_widget, stretch_last=True), "OverlayWidget")

    # EnumComboBox
    enum_combo_box = EnumComboBox(enum_class=EnumA)
    enum_combo_box_2 = EnumComboBox(enum_class=SettingEnum, allow_none=True)
    enum_combo_box_2.sig_current_enum_changed.connect(lambda value: print(f"Selected enum: {value}"))
    btn_toggle_none = QtWidgets.QPushButton("Toggle allowNone on second combo box")
    btn_toggle_none.clicked.connect(lambda: enum_combo_box_2.setAllowNone(not enum_combo_box_2.allowNone))
    tabs.addTab(_vbox_tab(btn_toggle_none, enum_combo_box, enum_combo_box_2), "EnumComboBox")

    # SettingCard
    setting_widget = EnumComboBox(enum_class=SettingEnum)
    setting_card = SettingCard(
        title="Example Setting",
        editor_widget=setting_widget,
        default_value=SettingEnum.DEFAULT,
        set_value_name="set_current_enum",
        description="This is a setting card with EnumComboBox as the editor widget",
        icon=get_icon("Settings"),
    )
    tabs.addTab(_vbox_tab(setting_card), "SettingCard")

    # DataTreeWidget / SearchableDataTreeWidget
    tabs.addTab(_vbox_tab(DataTreeWidget(data=_example_data()), stretch_last=True), "DataTreeWidget")
    searchable_data_tree = SearchableDataTreeWidget(allow_edit=True)
    searchable_data_tree.set_data(_example_data())
    tabs.addTab(_vbox_tab(searchable_data_tree, stretch_last=True), "SearchableDataTreeWidget")

    # DecimalSpinBox
    decimal_spin_box = DecimalSpinBox()
    decimal_spin_box.setRange(0, 100)
    decimal_spin_box.setDecimals(2)
    decimal_spin_box.setValue(50.25)
    decimal_spin_box.setSuffix(" mm")
    decimal_spin_box.setKeyboardTracking(False)

    output = QtWidgets.QTextEdit()
    output.setReadOnly(True)
    decimal_spin_box.valueChanged.connect(lambda value: output.append(str(value)))

    min_input = LabeledSlider(title="Minimum", title_pos=LabeledSlider.TitleLabelPosition.TOP_LEFT)
    min_input.setRange(-1_000, 1_000)
    min_input.setValue(0)
    min_input.valueChanged.connect(decimal_spin_box.setMinimum)

    max_input = LabeledSlider(title="Maximum", title_pos=LabeledSlider.TitleLabelPosition.TOP_CENTER)
    max_input.setRange(-1_000, 1_000)
    max_input.setValue(100)
    max_input.valueChanged.connect(decimal_spin_box.setMaximum)

    step_input = LabeledSlider(title="Step Size", title_pos=LabeledSlider.TitleLabelPosition.LEFT)
    step_input.setRange(1, 1_000)
    step_input.setValue(10)
    step_input.valueChanged.connect(decimal_spin_box.setSingleStep)

    decimals_input = LabeledSlider(title="Decimals", title_pos=LabeledSlider.TitleLabelPosition.LEFT)
    decimals_input.setRange(0, 6)
    decimals_input.setValue(2)
    decimals_input.valueChanged.connect(decimal_spin_box.setDecimals)

    kbdtracking_input = QtWidgets.QCheckBox("Keyboard Tracking")
    kbdtracking_input.toggled.connect(decimal_spin_box.setKeyboardTracking)

    correction_method_input = EnumComboBox(enum_class=QtWidgets.QAbstractSpinBox.CorrectionMode)
    correction_method_input.sig_current_enum_changed.connect(decimal_spin_box.setCorrectionMode)

    tabs.addTab(
        _vbox_tab(
            decimal_spin_box,
            output,
            min_input,
            max_input,
            step_input,
            decimals_input,
            kbdtracking_input,
            correction_method_input,
        ),
        "DecimalSpinBox",
    )

    # LabeledSlider
    labeled_slider_1 = LabeledSlider(title="Slider 1", title_pos=LabeledSlider.TitleLabelPosition.TOP_LEFT)
    labeled_slider_1.setRange(-1_000, 1_000)
    labeled_slider_2 = LabeledSlider(title="Slider 2", title_pos=LabeledSlider.TitleLabelPosition.BOTTOM_CENTER)
    labeled_slider_3 = LabeledSlider(title="Slider 3", title_pos=LabeledSlider.TitleLabelPosition.RIGHT)
    labeled_slider_3.setRange(0, 1000)
    labeled_slider_3.slider.setSingleStep(100)
    labeled_slider_3.slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
    tabs.addTab(_vbox_tab(labeled_slider_1, labeled_slider_2, labeled_slider_3), "LabeledSlider")

    # ColorPickerButton
    color_picker = ColorPickerButton()
    color_picker.setFlat(True)
    color_picker.sig_color_changed.connect(lambda color: print(f"Color 1: {color.name()}"))

    color_picker2 = ColorPickerButton(show_alpha=True, show_icon=False)
    color_picker2.sig_color_changed.connect(
        lambda color: print(f"Color 2: {color.name(QtGui.QColor.NameFormat.HexArgb)}")
    )

    btn_set_invalid_color = QtWidgets.QPushButton("Set Invalid Color (ignored)")
    btn_set_invalid_color.clicked.connect(lambda: color_picker.set_color(QtGui.QColor("invalid_color")))
    tabs.addTab(_vbox_tab(color_picker, color_picker2, btn_set_invalid_color), "ColorPickerButton")

    # ToggleSwitch / AnimatedToggleSwitch
    toggle = ToggleSwitch()
    animated_toggle = AnimatedToggleSwitch(checked_color="#1abc9c", pulse_checked_color="#4400B0EE")
    tabs.addTab(_vbox_tab(toggle, animated_toggle), "Toggle / AnimatedToggle")

    # CommandBar
    command_bar = CommandBar()
    action1 = QtGui.QAction(get_icon("MoreHorizontal"), "Action 1", command_bar)
    action2 = QtGui.QAction(get_icon("Settings"), "Action 2", command_bar)
    action3 = QtGui.QAction(get_icon("ArrowReset"), "Action 3", command_bar)
    for action in (action1, action2, action3):
        action.triggered.connect(lambda _=False, a=action: print(f"{a.text()} triggered"))
    command_bar.addActions([action1, action2])
    command_bar.addSeparator()
    command_bar.addAction(action3)

    fill_toggle = QtWidgets.QCheckBox("Fill")
    fill_toggle.setChecked(True)
    fill_toggle.toggled.connect(command_bar.set_fill)
    align_right = QtWidgets.QCheckBox("Align right (when not filling)")
    align_right.toggled.connect(
        lambda checked: command_bar.set_alignment(
            QtCore.Qt.AlignmentFlag.AlignRight if checked else QtCore.Qt.AlignmentFlag.AlignLeft
        )
    )
    tabs.addTab(_vbox_tab(command_bar, fill_toggle, align_right), "CommandBar")

    # ResizableMessageBox
    btn_info = QtWidgets.QPushButton("Information")
    btn_info.clicked.connect(lambda: ResizableMessageBox.information(window, "Information", "Everything is fine."))
    btn_question = QtWidgets.QPushButton("Question")
    btn_question.clicked.connect(
        lambda: print("Answer:", ResizableMessageBox.question(window, "Question", "Continue?"))
    )
    btn_exception = QtWidgets.QPushButton("Exception with traceback")
    btn_exception.clicked.connect(
        lambda: ResizableMessageBox.from_exception(
            window, "Unhandled Exception", "An unexpected error occurred.", _make_exception()
        )
    )
    tabs.addTab(_vbox_tab(btn_info, btn_question, btn_exception), "ResizableMessageBox")

    window.setCentralWidget(tabs)
    window.resize(1200, 800)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
