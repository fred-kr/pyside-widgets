import enum
import types

import numpy as np
from PySide6 import QtGui, QtWidgets

from pyside_widgets import (
    DataTreeWidget,
    DecimalSpinBox,
    EnumComboBox,
    GroupedComboBox,
    JupyterConsoleWindow,
    LabeledSlider,
    OverlayWidget,
    SearchableDataTreeWidget,
    SettingCard,
)


class EnumA(enum.Enum):
    A = 1
    B = 2
    C = 3


class SettingEnum(enum.Enum):
    DEFAULT = enum.auto()
    SETTING_A = enum.auto()
    SETTING_B = enum.auto()
    SETTING_C = enum.auto()


def example_func1() -> types.TracebackType | None:
    return example_func2()


def example_func2() -> types.TracebackType | None:
    try:
        raise ValueError("Some error")
    except ValueError:
        import sys

        return sys.exc_info()[2]


example_data = {
    "a list": [1, 2, 3, 4, 5, 6, {"nested1": "aaaaa", "nested2": "bbbbb"}, "seven"],
    "a dict": {"x": 1, "y": 2, "z": "three"},
    "an array": np.random.randint(10, size=(40, 10)),
    "a traceback": example_func2(),
    "a function": example_func1,
    "a class": DataTreeWidget,
}


def main() -> None:
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Widget Gallery")

    tab_widget = QtWidgets.QTabWidget()

    # GroupedComboBox
    grouped_cb_container = QtWidgets.QWidget()
    grouped_cb_layout = QtWidgets.QVBoxLayout(grouped_cb_container)
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
    grouped_cb_layout.addWidget(grouped_combo_box)
    grouped_cb_layout.addStretch()
    tab_widget.addTab(grouped_cb_container, "GroupedComboBox")

    # JupyterConsoleWindow
    jupyter_console = JupyterConsoleWindow("lightbg")
    jupyter_console.console.execute("print('Hello from Jupyter Console!')", True)
    tab_widget.addTab(jupyter_console, "JupyterConsoleWindow")

    # OverlayWidget
    base_widget = QtWidgets.QTextEdit("This is the base widget")
    overlay_widget = OverlayWidget(parent=base_widget)
    overlay_button = QtWidgets.QPushButton("Toggle Overlay")
    overlay_button.clicked.connect(
        lambda: overlay_widget.hide_overlay() if overlay_widget.isVisible() else overlay_widget.show_overlay()
    )
    overlay_button_container = QtWidgets.QWidget()
    layout_overlay = QtWidgets.QVBoxLayout(overlay_button_container)
    layout_overlay.addWidget(overlay_button)
    layout_overlay.addWidget(base_widget)

    tab_widget.addTab(overlay_button_container, "OverlayWidget")

    # EnumComboBox
    enum_cb_container = QtWidgets.QWidget()
    enum_cb_layout = QtWidgets.QVBoxLayout(enum_cb_container)
    enum_combo_box = EnumComboBox(EnumA)
    enum_cb_layout.addWidget(enum_combo_box)
    enum_cb_layout.addStretch()
    tab_widget.addTab(enum_cb_container, "EnumComboBox")

    # SettingCard
    setting_card_container = QtWidgets.QWidget()
    setting_card_layout = QtWidgets.QVBoxLayout(setting_card_container)
    setting_widget = EnumComboBox(SettingEnum)
    setting_card = SettingCard(
        title="Example Setting",
        editor_widget=setting_widget,
        description="This is a setting card with EnumComboBox as the editor widget",
        icon=QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.Computer),
        reset_button=True,
    )
    setting_card.sig_reset_clicked.connect(lambda: setting_widget.set_current_enum(SettingEnum.DEFAULT))
    setting_card_layout.addWidget(setting_card)
    setting_card_layout.addStretch()
    tab_widget.addTab(setting_card_container, "SettingCard")

    # DataTreeWidget
    data_tree_container = QtWidgets.QWidget()
    data_tree_layout = QtWidgets.QVBoxLayout(data_tree_container)
    data_tree = DataTreeWidget(data=example_data)
    data_tree_layout.addWidget(data_tree)
    data_tree_layout.addStretch()
    tab_widget.addTab(data_tree_container, "DataTreeWidget")

    # SearchableDataTreeWidget
    searchable_data_tree_container = QtWidgets.QWidget()
    searchable_data_tree_layout = QtWidgets.QVBoxLayout(searchable_data_tree_container)
    searchable_data_tree = SearchableDataTreeWidget()
    searchable_data_tree.set_data(example_data)
    searchable_data_tree_layout.addWidget(searchable_data_tree)
    searchable_data_tree_layout.addStretch()
    tab_widget.addTab(searchable_data_tree_container, "SearchableDataTreeWidget")

    # DecimalSpinBox
    decimal_spin_box_container = QtWidgets.QWidget()
    decimal_spin_box_layout = QtWidgets.QVBoxLayout()
    decimal_spin_box = DecimalSpinBox()
    decimal_spin_box.setRange(0, 100)
    decimal_spin_box.setDecimals(2)
    decimal_spin_box.setValue(50.25)

    output = QtWidgets.QTextEdit()
    output.setReadOnly(True)

    decimal_spin_box.valueChanged.connect(lambda value: output.append(str(value)))

    min_input = LabeledSlider(title="Minimum", title_pos=LabeledSlider.TitleLabelPosition.TOP_LEFT)
    min_input.setRange(-1_000, 1_000)
    min_input.setSingleStep(10)
    min_input.setValue(0)
    min_input.valueChanged.connect(decimal_spin_box.setMinimum)

    max_input = LabeledSlider(title="Maximum", title_pos=LabeledSlider.TitleLabelPosition.TOP_CENTER)
    # max_input.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)
    max_input.setRange(-1_000, 1_000)
    max_input.setSingleStep(10)
    max_input.setValue(100)
    max_input.valueChanged.connect(decimal_spin_box.setMaximum)

    step_input = LabeledSlider(title="Step Size", title_pos=LabeledSlider.TitleLabelPosition.LEFT)
    step_input.setRange(1, 1_000)
    step_input.setSingleStep(10)
    step_input.setValue(10)
    step_input.valueChanged.connect(decimal_spin_box.setSingleStep)

    controls_layout = QtWidgets.QVBoxLayout()
    controls_layout.addWidget(min_input)
    controls_layout.addWidget(max_input)
    controls_layout.addWidget(step_input)

    decimal_spin_box_layout.addWidget(decimal_spin_box)
    decimal_spin_box_layout.addWidget(output)
    decimal_spin_box_layout.addLayout(controls_layout)
    decimal_spin_box_layout.addStretch()
    decimal_spin_box_container.setLayout(decimal_spin_box_layout)

    tab_widget.addTab(decimal_spin_box_container, "DecimalSpinBox")

    # LabeledSlider
    labeled_slider_container = QtWidgets.QWidget()
    labeled_slider_layout = QtWidgets.QVBoxLayout()
    labeled_slider_1 = LabeledSlider(title="Slider 1", title_pos=LabeledSlider.TitleLabelPosition.TOP_LEFT)
    labeled_slider_1.setRange(-1_000, 1_000)
    labeled_slider_2 = LabeledSlider(title="Slider 2", title_pos=LabeledSlider.TitleLabelPosition.TOP_CENTER)
    labeled_slider_3 = LabeledSlider(title="Slider 3", title_pos=LabeledSlider.TitleLabelPosition.TOP_RIGHT)
    labeled_slider_3.setRange(0, 1000)
    labeled_slider_3.setSingleStep(100)
    labeled_slider_3.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
    labeled_slider_layout.addWidget(labeled_slider_1)
    labeled_slider_layout.addWidget(labeled_slider_2)
    labeled_slider_layout.addWidget(labeled_slider_3)
    labeled_slider_layout.addStretch()
    labeled_slider_container.setLayout(labeled_slider_layout)

    tab_widget.addTab(labeled_slider_container, "LabeledSlider")

    window.setCentralWidget(tab_widget)
    window.resize(1920, 1080)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
