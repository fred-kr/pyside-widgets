import os
from types import ModuleType

from PySide6.QtDesigner import QDesignerCustomWidgetInterface, QPyDesignerCustomWidgetCollection

plugins = []


def get_modules(py: ModuleType) -> list[QDesignerCustomWidgetInterface]:
    import inspect

    from PySide6.QtDesigner import QDesignerCustomWidgetInterface

    modules: list[QDesignerCustomWidgetInterface] = []
    for name, obj in inspect.getmembers(py, inspect.isclass):
        if name.endswith("Plugin"):
            obj_instance = obj()
            if isinstance(obj_instance, QDesignerCustomWidgetInterface):
                print(f"Loading {name}")
                modules.append(obj_instance)
    return modules


for filename in os.listdir("."):
    if filename.endswith(".py") and not filename.startswith("_"):
        py = __import__(f"{filename}".replace(".py", ""))
        for plug in get_modules(py):
            QPyDesignerCustomWidgetCollection.addCustomWidget(plug)
