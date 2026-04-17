from PySide6 import QtWidgets
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

from pyside_widgets.message_box import ResizableMessageBox
from pyside_widgets.plugins.plugin_base import PluginBase


class ContainerPlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " (Container)"

    def isContainer(self) -> bool:
        return True


class ResizableMessageBoxPlugin(ContainerPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        return ResizableMessageBox(
            title="Message",
            text="Message text",
            parent=parent,
        )

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='ResizableMessageBox' name='resizableMessageBox'>
                <property name='windowTitle'>
                    <string>Message</string>
                </property>
                <property name='text'>
                    <string>Message text</string>
                </property>
                <property name='icon'>
                    <number>0</number>
                </property>
                <property name='detail_text'>
                    <string></string>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "ResizableMessageBox"
