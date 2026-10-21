from PySide6 import QtWidgets
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

from pyside_widgets.message_box import ResizableMessageBox
from pyside_widgets.overlay_widget import OverlayWidget
from pyside_widgets.plugins.plugin_base import PluginBase


class ContainerPlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " (Container)"

    def isContainer(self) -> bool:
        return True


class ResizableMessageBoxPlugin(ContainerPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        return ResizableMessageBox(title="Message", text="Message text", parent=parent)

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
                    <number>1</number>
                </property>
                <property name='detail_text'>
                    <string></string>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "ResizableMessageBox"


class OverlayWidgetPlugin(ContainerPlugin, QDesignerCustomWidgetInterface):
    def isContainer(self) -> bool:
        return False

    def createWidget(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        return OverlayWidget(parent=parent)

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='OverlayWidget' name='overlayWidget'>
                <property name='text'>
                    <string>Running...</string>
                </property>
                <property name='bg_color'>
                    <color alpha='128'>
                        <red>0</red>
                        <green>0</green>
                        <blue>0</blue>
                    </color>
                </property>
                <property name='bar_color'>
                    <color alpha='255'>
                        <red>100</red>
                        <green>149</green>
                        <blue>237</blue>
                    </color>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "OverlayWidget"

    def toolTip(self) -> str:
        return "Covers and disables its parent widget while an operation is running"
