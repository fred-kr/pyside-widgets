from PySide6.QtDesigner import QDesignerCustomWidgetInterface
from PySide6.QtWidgets import QComboBox, QWidget

from pyside_widgets.color_picker_button import ColorPickerButton
from pyside_widgets.decimal_spin_box import DecimalSpinBox
from pyside_widgets.enum_combo_box import EnumComboBox
from pyside_widgets.plugins.plugin_base import PluginBase
from pyside_widgets.toggle_switch import ToggleSwitch


class InputPlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " (Inputs)"


class ColorPickerButtonPlugin(InputPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QWidget) -> QWidget:
        return ColorPickerButton(parent=parent)

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='ColorPickerButton' name='colorPickerButton'>
                <property name='showAlphaChannel'>
                    <bool>false</bool>
                </property>
                <property name='showAsIcon'>
                    <bool>true</bool>
                </property>
                <property name='showText'>
                    <bool>false</bool>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "ColorPickerButton"


class DecimalSpinBoxPlugin(InputPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QWidget) -> QWidget:
        return DecimalSpinBox(parent=parent)

    # def domXml(self) -> str:
    #     return """
    #     <ui language='c++'>
    #         <widget class='DecimalSpinBox' name='decimalSpinBox'>
    #         </widget>
    #     </ui>
    #     """

    def name(self) -> str:
        return "DecimalSpinBox"


class EnumComboBoxPlugin(InputPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QWidget) -> QWidget:
        return EnumComboBox(parent=parent, enum_class=QComboBox.InsertPolicy)

    def domXml(self) -> str:
        return """
        <ui language='c++'>
            <widget class='EnumComboBox' name='enumComboBox'>
                <property name='allowNone'>
                    <bool>false</bool>
                </property>
            </widget>
        </ui>
        """

    def name(self) -> str:
        return "EnumComboBox"

    def toolTip(self) -> str:
        return "QComboBox variant that uses a python Enum class to populate the combo box items."

    def whatsThis(self) -> str:
        return self.toolTip()


class ToggleSwitchPlugin(InputPlugin, QDesignerCustomWidgetInterface):
    def createWidget(self, parent: QWidget) -> ToggleSwitch:
        return ToggleSwitch(parent=parent)

    # def domXml(self) -> str:
    #     return """
    #     <ui language='c++'>
    #         <widget class='ToggleSwitch' name='toggleSwitch'>
    #         </widget>
    #     </ui>
    #     """

    def name(self) -> str:
        return "ToggleSwitch"

    def toolTip(self) -> str:
        return "QCheckBox displayed as a toggle switch"

    def whatsThis(self) -> str:
        return self.toolTip()
