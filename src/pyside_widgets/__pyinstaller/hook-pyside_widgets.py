# PyInstaller hook: ship the SVG icons that pyside_widgets._icons loads through importlib.resources.
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("pyside_widgets", includes=["icons/*.svg"])
