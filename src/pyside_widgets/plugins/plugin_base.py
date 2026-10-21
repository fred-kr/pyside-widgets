import re

from PySide6.QtDesigner import QDesignerFormEditorInterface
from PySide6.QtGui import QIcon

_CAMEL_CASE_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


class PluginBase:
    """
    Defaults shared by the Designer plugins.

    Subclasses combine it with ``QDesignerCustomWidgetInterface`` and implement ``createWidget``, ``name`` and,
    usually, ``domXml``.
    """

    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    def initialize(self, editor: QDesignerFormEditorInterface) -> None:
        self._initialized = True

    def isInitialized(self) -> bool:
        return self._initialized

    def icon(self) -> QIcon:
        return QIcon()

    def name(self) -> str:
        return "PluginBase"

    def group(self) -> str:
        return "pyside-widgets"

    def toolTip(self) -> str:
        words = _CAMEL_CASE_BOUNDARY.sub(" ", self.name())
        return words[0].upper() + words[1:].lower()

    def whatsThis(self) -> str:
        return self.toolTip()

    def isContainer(self) -> bool:
        return False

    def domXml(self) -> str:
        return f'<widget class="{self.name()}" name="{self.name()}"></widget>'

    def includeFile(self) -> str:
        return "pyside_widgets"
