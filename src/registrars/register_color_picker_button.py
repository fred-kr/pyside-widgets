from PySide6 import QtDesigner

from pyside_widgets.color_picker_button import ColorPickerButton

DOM_XML = """
<ui language="c++">
    <widget class="ColorPickerButton" name="ColorPickerButton">
        <property name="geometry">
            <rect>
                <x>0</x>
                <y>0</y>
                <width>100</width>
                <height>100</height>
            </rect>
        </property>
    </widget>
</ui>
"""

QtDesigner.QPyDesignerCustomWidgetCollection.registerCustomWidget(
    ColorPickerButton, DOM_XML, tool_tip="Color Picker Button", group="PySide6 Widgets", module="pyside_widgets"
)
