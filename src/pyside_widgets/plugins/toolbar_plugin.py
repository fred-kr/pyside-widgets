from PySide6.QtDesigner import QDesignerCustomWidgetInterface
from PySide6.QtWidgets import QWidget

from pyside_widgets.command_bar import CommandBar
from pyside_widgets.plugins.plugin_base import PluginBase


class ToolBarPlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " / Toolbars"


class CommandBarPlugin(PluginBase, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QWidget) -> CommandBar:
        return CommandBar(parent=parent)

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='CommandBar' name='commandBar'>
                <property name='fill'>
                    <bool>true</bool>
                </property>
                <property name='alignment'>
                    <enum>AlignLeft</enum>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "CommandBar"
