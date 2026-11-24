"""
Every widget offered in Qt Designer must survive what Designer and pyside6-uic do with it: construct it as
``Widget(parent)`` and set the properties named in its DOM XML by name.
"""

import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QWidget

import pyside_widgets
from pyside_widgets import IndeterminateSpinner, OverlayWidget, ValueSlider
from pyside_widgets.examples import designer
from pyside_widgets.plugins import register_widgets
from pyside_widgets.plugins.register_widgets import DESIGNER_WIDGETS, MODULE, DesignerWidget

_IDS = [entry.widget.__name__ for entry in DESIGNER_WIDGETS]


@pytest.mark.parametrize("entry", DESIGNER_WIDGETS, ids=_IDS)
def test_widget_is_constructible_with_only_a_parent(qtbot, entry: DesignerWidget):
    host = QWidget()
    qtbot.addWidget(host)
    widget = entry.widget(host)
    assert widget.parent() is host


@pytest.mark.parametrize("entry", DESIGNER_WIDGETS, ids=_IDS)
def test_xml_is_well_formed_and_names_existing_properties(qtbot, entry: DesignerWidget):
    root = ET.fromstring(entry.dom_xml())
    widget_node = root.find("widget")
    assert widget_node is not None
    assert widget_node.get("class") == entry.widget.__name__

    widget = entry.widget()
    qtbot.addWidget(widget)
    meta_object = widget.metaObject()
    for property_node in widget_node.findall("property"):
        name = property_node.get("name")
        assert name is not None
        assert meta_object.indexOfProperty(name) >= 0, f"{entry.widget.__name__} has no Qt property {name!r}"


@pytest.mark.parametrize("entry", DESIGNER_WIDGETS, ids=_IDS)
def test_widget_is_importable_from_the_header_module(entry: DesignerWidget):
    """uic writes ``from pyside_widgets import <class>`` for the ``<header>`` the registry announces."""
    assert MODULE == pyside_widgets.__name__
    assert getattr(pyside_widgets, entry.widget.__name__) is entry.widget


def _own_designable_properties(widget: QWidget) -> list[str]:
    meta_object = widget.metaObject()
    properties = [meta_object.property(i) for i in range(meta_object.propertyOffset(), meta_object.propertyCount())]
    return [str(prop.name()) for prop in properties if prop.isDesignable() and prop.isWritable()]


@pytest.mark.parametrize(
    "widget_class",
    [*(entry.widget for entry in DESIGNER_WIDGETS), OverlayWidget, IndeterminateSpinner, ValueSlider],
    ids=lambda cls: cls.__name__,
)
def test_every_designable_property_has_the_setter_uic_calls(qtbot, widget_class):
    """pyside6-uic writes ``widget.setFooBar(value)`` for a property ``fooBar``; it never uses ``setProperty``."""
    host = QWidget()
    qtbot.addWidget(host)
    widget = widget_class(host)
    for name in _own_designable_properties(widget):
        setter = "set" + name[0].upper() + name[1:]
        assert callable(getattr(widget, setter, None)), f"{widget_class.__name__}.{setter}() is missing"


def _form_xml() -> str:
    """A form holding every registered widget exactly as Designer would save it after a drop from the widget box."""
    items = []
    custom_widgets = []
    for entry in DESIGNER_WIDGETS:
        widget_node = ET.fromstring(entry.dom_xml()).find("widget")
        assert widget_node is not None
        items.append(f"<item>{ET.tostring(widget_node, encoding='unicode')}</item>")
        custom_widgets.append(
            f"<customwidget><class>{entry.widget.__name__}</class><extends>QWidget</extends>"
            f"<header>{MODULE}</header></customwidget>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?><ui version="4.0"><class>Form</class>'
        '<widget class="QWidget" name="Form"><layout class="QVBoxLayout" name="formLayout">'
        f"{''.join(items)}</layout></widget><customwidgets>{''.join(custom_widgets)}</customwidgets></ui>"
    )


def test_generated_ui_code_runs(qtbot, tmp_path):
    """End to end: Designer XML -> pyside6-uic -> the generated ``setupUi`` builds every widget and sets its values."""
    uic = shutil.which("pyside6-uic", path=str(Path(sys.executable).parent)) or shutil.which("pyside6-uic")
    if uic is None:
        pytest.skip("pyside6-uic not found")
    ui_file = tmp_path / "form.ui"
    ui_file.write_text(_form_xml(), encoding="utf-8")
    generated = subprocess.run([uic, str(ui_file)], capture_output=True, text=True, check=True).stdout
    assert f"from {MODULE} import" in generated

    namespace: dict[str, Any] = {}
    exec(compile(generated, "ui_form.py", "exec"), namespace)
    form = QWidget()
    qtbot.addWidget(form)
    ui = namespace["Ui_Form"]()
    ui.setupUi(form)

    for entry in DESIGNER_WIDGETS:
        name = entry.widget.__name__
        assert isinstance(getattr(ui, name[0].lower() + name[1:]), entry.widget)
    assert ui.settingCard.get_title() == "Setting Card"
    assert ui.settingCard.get_reset_shown() is True
    assert ui.decimalSpinBox.maximum() == Decimal("100.0")
    assert ui.decimalSpinBox.singleStep() == Decimal("1.0")
    assert ui.colorPickerButton.get_show_text() is True
    assert ui.enumComboBox.get_allow_none() is False
    assert ui.labeledSlider.get_title() == "Title"
    assert ui.commandBar.get_fill() is True


def test_dialogs_and_overlays_are_not_offered():
    names = set(_IDS)
    assert "ResizableMessageBox" not in names  # a dialog is not a child of a form
    assert "OverlayWidget" not in names  # hides itself and positions itself outside any layout


def test_launcher_appends_to_an_existing_plugin_path(monkeypatch):
    monkeypatch.setenv("PYSIDE_DESIGNER_PLUGINS", "some-other-plugins")
    paths = designer.designer_environment()["PYSIDE_DESIGNER_PLUGINS"].split(os.pathsep)
    assert paths[0] == "some-other-plugins"
    assert os.path.isfile(os.path.join(paths[1], "register_widgets.py"))

    monkeypatch.delenv("PYSIDE_DESIGNER_PLUGINS")
    assert os.pathsep not in designer.designer_environment()["PYSIDE_DESIGNER_PLUGINS"]


def test_launcher_makes_the_package_importable_for_designer(monkeypatch):
    """Designer's embedded interpreter ignores .pth files, so an editable install needs an explicit PYTHONPATH."""
    monkeypatch.setenv("PYTHONPATH", "already-there")
    paths = designer.designer_environment()["PYTHONPATH"].split(os.pathsep)
    assert paths[0] == "already-there"
    assert os.path.isfile(os.path.join(paths[1], "pyside_widgets", "__init__.py"))


def test_plugin_script_runs_without_dunder_file():
    """Designer executes the text of register_widgets.py; ``__file__`` is not defined there."""
    source = Path(register_widgets.__file__).read_text(encoding="utf-8")
    assert "__file__" not in source
