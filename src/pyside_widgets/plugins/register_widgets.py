"""
Entry point loaded by Qt Designer (``PYSIDE_DESIGNER_PLUGINS`` points at this directory).

Registers every widget listed in ``DESIGNER_WIDGETS``. To add a widget, add a row; nothing else is needed.

What Designer and ``pyside6-uic`` require of a listed class:

- It is created as ``Widget(parent)``, so the parent is its first argument and no other argument is required.
- A property ``fooBar`` set in Designer becomes the call ``widget.setFooBar(value)`` in generated code, so every
  designable Qt property needs a method of that name.

Designer executes the text of this file inside its own interpreter. The file path is not available there (do not use
the module's file attribute), and ``pyside_widgets`` must be importable: the ``pyside-widgets-designer`` launcher sets
``PYTHONPATH`` for that, because the interpreter ignores the ``.pth`` file of an editable install.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import NamedTuple

from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection
from PySide6.QtWidgets import QWidget

from pyside_widgets import (
    AnimatedToggleSwitch,
    ColorPickerButton,
    CommandBar,
    DataTreeWidget,
    DecimalSpinBox,
    EnumComboBox,
    GroupedComboBox,
    LabeledSlider,
    SearchableDataTreeWidget,
    SettingCard,
    ToggleSwitch,
)

MODULE = "pyside_widgets"
"""Written to the ``<header>`` of a form, so ``pyside6-uic`` imports every widget from the package root."""

_INPUTS = "pyside-widgets (Inputs)"
_DISPLAY = "pyside-widgets (Display)"
_COMPOSITE = "pyside-widgets (Composite)"
_TOOLBAR = "pyside-widgets (ToolBar)"

_NO_PROPERTIES: Mapping[str, str] = MappingProxyType({})


class DesignerWidget(NamedTuple):
    """One entry of Designer's widget box."""

    widget: type[QWidget]
    group: str
    tool_tip: str
    properties: Mapping[str, str] = _NO_PROPERTIES
    """Qt property name -> DOM XML of the value a newly dropped widget starts with."""

    def dom_xml(self) -> str:
        class_name = self.widget.__name__
        object_name = class_name[0].lower() + class_name[1:]
        properties = "".join(f"<property name='{name}'>{value}</property>" for name, value in self.properties.items())
        return f"<ui language='c++'><widget class='{class_name}' name='{object_name}'>{properties}</widget></ui>"


DESIGNER_WIDGETS: tuple[DesignerWidget, ...] = (
    DesignerWidget(
        ColorPickerButton,
        _INPUTS,
        "Button that shows a color and opens a color dialog when clicked",
        {
            "showAlphaChannel": "<bool>false</bool>",
            "showAsIcon": "<bool>true</bool>",
            "showText": "<bool>true</bool>",
        },
    ),
    DesignerWidget(
        DecimalSpinBox,
        _INPUTS,
        "Spin box backed by decimal.Decimal",
        {
            "decimalPlaces": "<number>2</number>",
            "minimumValue": "<double>0.0</double>",
            "maximumValue": "<double>100.0</double>",
            "stepSize": "<double>1.0</double>",
        },
    ),
    DesignerWidget(
        EnumComboBox,
        _INPUTS,
        "Combo box populated from a python Enum class. Empty until set_enum_class() is called in code.",
        {"allowNone": "<bool>false</bool>"},
    ),
    DesignerWidget(GroupedComboBox, _INPUTS, "Combo box with group headers. Filled in code."),
    DesignerWidget(
        LabeledSlider,
        _INPUTS,
        "Slider with a title, minimum/maximum labels and the value above the handle",
        {"title": "<string>Title</string>"},
    ),
    DesignerWidget(ToggleSwitch, _INPUTS, "Check box drawn as a toggle switch"),
    DesignerWidget(AnimatedToggleSwitch, _INPUTS, "Check box drawn as an animated toggle switch"),
    DesignerWidget(DataTreeWidget, _DISPLAY, "Tree view of nested python data. Filled in code with set_data()."),
    DesignerWidget(
        SearchableDataTreeWidget, _DISPLAY, "Data tree with a search box and a sort button. Filled in code."
    ),
    DesignerWidget(
        SettingCard,
        _COMPOSITE,
        "Card with icon, title, description and reset button. The editor is added in code with set_editor_widget().",
        {
            "title": "<string>Setting Card</string>",
            "description": "<string></string>",
            "resetShown": "<bool>true</bool>",
        },
    ),
    DesignerWidget(
        CommandBar,
        _TOOLBAR,
        "Toolbar whose buttons fill the width or align to one side",
        {"fill": "<bool>true</bool>"},
    ),
)

for _entry in DESIGNER_WIDGETS:
    QPyDesignerCustomWidgetCollection.registerCustomWidget(
        _entry.widget,
        module=MODULE,
        group=_entry.group,
        tool_tip=_entry.tool_tip,
        xml=_entry.dom_xml(),
    )
