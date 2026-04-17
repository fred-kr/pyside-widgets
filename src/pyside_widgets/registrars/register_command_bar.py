from PySide6 import QtDesigner

from pyside_widgets.command_bar import CommandBar  # noqa: F401 # type: ignore,
from pyside_widgets.plugins.toolbar_plugin import CommandBarPlugin

if __name__ == "__main__":
    QtDesigner.QPyDesignerCustomWidgetCollection.addCustomWidget(CommandBarPlugin())
