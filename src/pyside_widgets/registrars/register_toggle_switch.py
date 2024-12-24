from PySide6 import QtDesigner

from pyside_widgets.toggle_switch import (
    Toggle,  # noqa: F401 # type: ignore
    TogglePlugin,
)

if __name__ == "__main__":
    QtDesigner.QPyDesignerCustomWidgetCollection.addCustomWidget(TogglePlugin())
