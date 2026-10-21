"""
Entry point loaded by Qt Designer (``PYSIDE_DESIGNER_PLUGINS`` points at this directory).

Registers every ``*Plugin`` class from the plugin modules. Imports are absolute, so it works from any working directory
as long as ``pyside_widgets`` is installed in the interpreter Designer uses.
"""

import inspect

from PySide6.QtDesigner import QDesignerCustomWidgetInterface, QPyDesignerCustomWidgetCollection

from pyside_widgets.plugins import composite_plugin, container_plugin, input_plugin, toolbar_plugin

for module in (input_plugin, composite_plugin, container_plugin, toolbar_plugin):
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if (
            name.endswith("Plugin")
            and issubclass(cls, QDesignerCustomWidgetInterface)
            and cls.__module__ == module.__name__
            and not inspect.isabstract(cls)
        ):
            QPyDesignerCustomWidgetCollection.addCustomWidget(cls())
