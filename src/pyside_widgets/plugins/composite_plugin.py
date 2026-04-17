from PySide6 import QtWidgets
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

from pyside_widgets._style_sheets import CARD_STYLE_SHEET
from pyside_widgets.plugins.plugin_base import PluginBase
from pyside_widgets.setting_card_widget import SettingCard


class CompositePlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " (Composite)"


class SettingCardPlugin(CompositePlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        return SettingCard(
            title="Setting Card",
            parent=parent,
        )

    def domXml(self) -> str:
        return f"""
        <ui language='c++'>
            <widget class='SettingCard' name='settingCard'>
                <property name='title'>
                    <string>Setting Card</string>
                </property>
                <property name='description'>
                    <string></string>
                </property>
                <property name='icon'>
                    <iconset>
                        <normaloff>icons/ArrowReset.svg</normaloff>
                    </iconset>
                </property>
                <property name='reset_shown'>
                    <bool>true</bool>
                </property>
                <property name='icon_size'>
                    <size>
                        <width>16</width>
                        <height>16</height>
                    </size>
                </property>
                <property name='styleSheet'>
                    <string notr='true'>{CARD_STYLE_SHEET}
                    </string>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "SettingCard"
