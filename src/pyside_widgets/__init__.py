"""Custom PySide6 widgets.

Everything is importable from this package. ``JupyterConsoleWindow`` and ``JupyterConsoleWidget`` are loaded on first
access because they need the optional ``qtconsole`` dependency (``pip install "pyside-widgets[jupyter]"``).
"""

from importlib import import_module
from typing import TYPE_CHECKING

from pyside_widgets.color_picker_button import ColorPickerButton
from pyside_widgets.command_bar import CommandBar
from pyside_widgets.data_tree_widget import DataTreeWidget, SearchableDataTreeWidget
from pyside_widgets.decimal_spin_box import DecimalSpinBox
from pyside_widgets.enum_combo_box import EnumComboBox
from pyside_widgets.grouped_combo_box import GroupedComboBox
from pyside_widgets.labeled_slider import LabeledSlider
from pyside_widgets.message_box import ResizableMessageBox
from pyside_widgets.overlay_widget import OverlayWidget
from pyside_widgets.setting_card_widget import SettingCard
from pyside_widgets.toggle_switch import AnimatedToggleSwitch, ToggleSwitch

if TYPE_CHECKING:
    from pyside_widgets.jupyter_console_widget import JupyterConsoleWidget, JupyterConsoleWindow

__all__ = [
    "AnimatedToggleSwitch",
    "ColorPickerButton",
    "CommandBar",
    "DataTreeWidget",
    "DecimalSpinBox",
    "EnumComboBox",
    "GroupedComboBox",
    "JupyterConsoleWidget",
    "JupyterConsoleWindow",
    "LabeledSlider",
    "OverlayWidget",
    "ResizableMessageBox",
    "SearchableDataTreeWidget",
    "SettingCard",
    "ToggleSwitch",
]

_LAZY_ATTRIBUTES = {
    "JupyterConsoleWidget": "pyside_widgets.jupyter_console_widget",
    "JupyterConsoleWindow": "pyside_widgets.jupyter_console_widget",
}


def __getattr__(name: str) -> object:
    module_name = _LAZY_ATTRIBUTES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module_name), name)


def __dir__() -> list[str]:
    return sorted({*globals(), *_LAZY_ATTRIBUTES})
