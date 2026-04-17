from PySide6 import QtDesigner

from pyside_widgets.plugins.container_plugin import SettingCardPlugin
from pyside_widgets.setting_card_widget import SettingCard  # noqa: F401 # type: ignore,

if __name__ == "__main__":
    QtDesigner.QPyDesignerCustomWidgetCollection.addCustomWidget(SettingCardPlugin())
