# pyside-widgets

Custom PySide6 widgets extracted from the [Signal Viewer](https://github.com/fred-kr/signal-viewer) app, plus Qt
Designer plugins for them. The only runtime dependency is `pyside6`.

```python
from PySide6.QtWidgets import QApplication
from pyside_widgets import DecimalSpinBox

app = QApplication([])
spin_box = DecimalSpinBox()
spin_box.setRange(0, 10)
spin_box.setDecimals(3)
spin_box.setValue("0.125")
spin_box.valueChanged.connect(print)  # prints decimal.Decimal values
spin_box.show()
app.exec()
```

## Install

```sh
pip install pyside-widgets
pip install "pyside-widgets[jupyter]"   # adds qtconsole for JupyterConsoleWindow
```

`JupyterConsoleWindow` and `JupyterConsoleWidget` are imported lazily. `import pyside_widgets` never loads
`qtconsole`, and accessing either name without the extra raises `ImportError`.

## Widgets

| Widget | Base class | Purpose |
|---|---|---|
| `DecimalSpinBox` | `QAbstractSpinBox` | Spin box backed by `decimal.Decimal` with range clamping and configurable precision. |
| `EnumComboBox` | `QComboBox` | Combo box populated from a python `Enum`, with an optional "no selection" row. |
| `ToggleSwitch`, `AnimatedToggleSwitch` | `QCheckBox` | Check box drawn as a toggle switch, optionally animated. |
| `ColorPickerButton` | `QPushButton` | Button that shows a color and opens `QColorDialog`. |
| `LabeledSlider` | `QWidget` | Slider with title, min/max labels and the current value drawn above the handle. |
| `GroupedComboBox` | `QComboBox` | Combo box with bold group headers and separators. |
| `CommandBar` | `QToolBar` | Toolbar whose buttons fill the width or align to one side. |
| `SettingCard` | `QFrame` | Card with icon, title, description, editor widget and reset button. |
| `DataTreeWidget`, `SearchableDataTreeWidget` | `QTreeWidget`, `QWidget` | Tree view of nested dicts, lists, arrays and tracebacks, with search and sort. |
| `OverlayWidget` | `QWidget` | Translucent overlay with spinner that covers and disables its parent. |
| `ResizableMessageBox` | `QDialog` | Resizable `QMessageBox` replacement with selectable text and a collapsible detail section. |
| `JupyterConsoleWindow` | `QWidget` | In-process Jupyter console (needs the `jupyter` extra). |

Array support in `DataTreeWidget` is duck-typed on `shape`, `dtype` and `__array__`, so numpy arrays work without
numpy being a dependency of this package.

## Qt Designer

Designer plugins live in `pyside_widgets/plugins`. Start Designer with them registered:

```sh
uv run designer
```

Forms reference the widgets with `<header>pyside_widgets</header>`, so `pyside6-uic` output imports them from the
package root. `DecimalSpinBox` exposes `decimalPlaces`, `minimumValue`, `maximumValue` and `stepSize` as Designer
properties; the Python accessors keep the Qt names (`decimals()`, `minimum()`, ...).

## Development

```sh
uv sync --group dev --extra jupyter
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run pyright
uv run demo        # widget gallery
```

Tests use `pytest-qt` and run offscreen (`QT_QPA_PLATFORM=offscreen` is set in `tests/conftest.py`).
