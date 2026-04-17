import re

from PySide6.QtDesigner import QDesignerFormEditorInterface
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


class PluginBase:
    Factory = None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__()
        self.initialized = False
        self.factory = None
        self.pattern = re.compile(r"(?<!^)(?=[A-Z])")

    def initialize(self, editor: QDesignerFormEditorInterface) -> None:
        if self.initialized:
            return

        self.initialized = True
        if not self.Factory:
            return

        manager = editor.extensionManager()
        self.factory = self.Factory(manager)
        manager.registerExtensions(self.factory, self.factory.IID)

    def isInitialized(self) -> bool:
        return self.initialized

    def icon(self) -> QIcon:
        return QIcon()

    def name(self) -> str:
        return "PluginBase"

    def group(self) -> str:
        return "pyside-widgets"

    def toolTip(self) -> str:
        name = self.pattern.sub(" ", self.name()).lower()
        return name[0].upper() + name[1:]

    def whatsThis(self) -> str:
        return self.toolTip()

    def isContainer(self) -> bool:
        return False

    def domXml(self) -> str:
        return f'<widget class="{self.name()}" name="{self.name()}"></widget>'

    def includeFile(self) -> str:
        return "pyside_widgets"
