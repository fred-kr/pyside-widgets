from PySide6 import QtDesigner

from pyside_widgets.color_picker_button import ColorPickerButton  # noqa: F401 # type: ignore,
from pyside_widgets.plugins.input_plugin import ColorPickerButtonPlugin

if __name__ == "__main__":
    QtDesigner.QPyDesignerCustomWidgetCollection.addCustomWidget(ColorPickerButtonPlugin())
