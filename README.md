# pyside-widgets

Custom PySide6 widgets extracted from the [Signal Viewer](https://github.com/fred-kr/signal-viewer) app, plus Qt
Designer plugins for them. The package is for developers of PySide6 applications who need one of the widgets listed
below. The only runtime dependency is `pyside6`.

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

Requires Python 3.14 or later and PySide6 6.12 or later.

## Install

```sh
pip install pyside-widgets
pip install "pyside-widgets[jupyter]"   # adds qtconsole for JupyterConsoleWindow
```

`JupyterConsoleWindow` and `JupyterConsoleWidget` are imported lazily. `import pyside_widgets` never loads
`qtconsole`, and accessing either name without the extra raises `ImportError`.

## Widgets

Import every widget from the package root: `from pyside_widgets import SettingCard`.

| Widget | Base class | Purpose |
|---|---|---|
| `DecimalSpinBox` | `QAbstractSpinBox` | Spin box backed by `decimal.Decimal` with range clamping and configurable precision. |
| `EnumComboBox` | `QComboBox` | Combo box populated from a python `Enum`, with an optional "no selection" row. |
| `ToggleSwitch`, `AnimatedToggleSwitch` | `QCheckBox` | Check box drawn as a toggle switch, optionally animated. |
| `ColorPickerButton` | `QPushButton` | Button that shows a color and opens `QColorDialog`. |
| `LabeledSlider`, `ValueSlider` | `QWidget`, `QSlider` | Slider with the current value drawn above the handle; `LabeledSlider` adds a title and min/max labels. |
| `GroupedComboBox` | `QComboBox` | Combo box with bold group headers and separators that cannot be selected. |
| `CommandBar` | `QToolBar` | Toolbar whose buttons fill the width or align to one side. |
| `SettingCard` | `QFrame` | Card with icon, title, description, editor widget and reset button. |
| `DataTreeWidget`, `SearchableDataTreeWidget` | `QTreeWidget`, `QWidget` | Tree view of nested dicts, lists, arrays and tracebacks, with search and sort. |
| `OverlayWidget`, `IndeterminateSpinner` | `QWidget` | Translucent overlay with spinner that covers and disables its parent; the spinner is usable on its own. |
| `ResizableMessageBox` | `QDialog` | Resizable `QMessageBox` replacement with selectable text and a collapsible detail section. |
| `JupyterConsoleWindow` | `QWidget` | In-process Jupyter console (needs the `jupyter` extra). |

Array support in `DataTreeWidget` is duck-typed on `shape`, `dtype` and `__array__`, so numpy arrays work without
numpy being a dependency of this package.

## Reset the editor of a SettingCard

A `SettingCard` does not know how to reset its editor. It emits `sig_reset_clicked`; you connect the reset.

```python
from PySide6.QtWidgets import QApplication, QSpinBox
from pyside_widgets import SettingCard

app = QApplication([])
spin_box = QSpinBox()
spin_box.setRange(1, 48_000)
spin_box.setValue(44_100)

card = SettingCard(title="Sampling rate", description="Samples per second", editor_widget=spin_box)
card.sig_reset_clicked.connect(lambda: spin_box.setValue(1_000))
card.btn_reset.click()
print(spin_box.value())
```

```text
1000
```

## Compare the answer of a ResizableMessageBox

The static helpers return a `QMessageBox.StandardButton`, like the `QMessageBox` helpers they replace.

```python
from PySide6.QtWidgets import QApplication, QMessageBox
from pyside_widgets import ResizableMessageBox

app = QApplication([])
answer = ResizableMessageBox.question(None, "Unsaved changes", "Save before closing?")
if answer == QMessageBox.StandardButton.Yes:
    print("saving")
```

Compare with members of `QMessageBox.StandardButton`. A member of `QDialogButtonBox.StandardButton` never compares
equal to it, although both enums have the same names and values. You can pass either enum as the `buttons` argument.

## Conventions every widget follows

These rules hold for every widget in the package. Follow them when you add one.

| Item | Rule | Reason |
|---|---|---|
| Constructor | `parent` is the first parameter. Every other parameter is keyword-only. | Designer and `pyside6-uic` create a widget as `Widget(parent)`. |
| Mirrored API | A method that mirrors the Qt class a widget replaces keeps the Qt name: `DecimalSpinBox.setValue`, `LabeledSlider.setRange`. | The widget is a drop-in replacement. |
| Added API | Methods are snake_case. Signals are named `sig_<name>`. | One style for everything the package adds. |
| Qt properties | A property is camelCase and has the accessors `get_x()` and `set_x()`, plus `setX` as a second name of the setter. | `pyside6-uic` writes a Designer property `fooBar` as the call `setFooBar(value)`. It does not use `setProperty`. |
| Value widgets | One property is the USER property and has a change signal: `ColorPickerButton.color`, `EnumComboBox.currentEnum`, `DecimalSpinBox.decimalValue`, `LabeledSlider.sliderValue`. | Item delegates and `QDataWidgetMapper` read and write an editor through its USER property. |
| Styling | No widget calls `setStyleSheet`. Colors come from the palette, fonts from the widget font, custom drawing happens in `paintEvent`. | A style sheet on a widget cascades into its children and replaces the application's own style sheet for that widget. |

Two consequences are worth knowing:

- A PySide `Property` occupies the class attribute of its name. `button.color` is therefore the color itself, not a
  method. Where a widget mirrors a Qt method of that name, the property has a different name: `DecimalSpinBox` keeps
  `value()` and names the property `decimalValue`.
- From Python, read and write a property by name with `widget.property("currentEnum")` and
  `widget.setProperty("currentEnum", member)`. `QMetaProperty.write()` converts an enum member to its plain value
  before the widget sees it.

## Qt Designer

Start Designer with the plugins registered:

```sh
uv run pyside-widgets-designer
```

The launcher appends the plugin directory to `PYSIDE_DESIGNER_PLUGINS` and the package location to `PYTHONPATH`. The
second part matters for a development checkout: Designer's embedded interpreter ignores the `.pth` file of an
editable install, so without it the plugins fail with `ModuleNotFoundError: No module named 'pyside_widgets'` and
Designer shows no custom widgets. If you start `pyside6-designer` yourself, set both variables.

The widget box lists `ColorPickerButton`, `DecimalSpinBox`, `EnumComboBox`, `GroupedComboBox`, `LabeledSlider`,
`ToggleSwitch`, `AnimatedToggleSwitch`, `DataTreeWidget`, `SearchableDataTreeWidget`, `SettingCard` and
`CommandBar`. `ResizableMessageBox` and `OverlayWidget` are not listed: a dialog is not a child of a form, and an
overlay positions itself outside any layout. Create both in code.

Forms reference the widgets with `<header>pyside_widgets</header>`, so `pyside6-uic` output imports them from the
package root. `DecimalSpinBox` exposes `decimalPlaces`, `minimumValue`, `maximumValue` and `stepSize` as Designer
properties; the Python accessors keep the Qt names (`decimals()`, `minimum()`, ...).

To list a new widget, add one row to `DESIGNER_WIDGETS` in
[register_widgets.py](src/pyside_widgets/plugins/register_widgets.py). `tests/test_designer_plugins.py` then checks
that the widget meets the constructor and setter rules above and that `pyside6-uic` output for it runs.

## Known limitations

- `ToggleSwitch` draws no label. `setText()` is accepted and ignored. Put a `QLabel` next to the switch.
- `DataTreeWidget(allow_edit=True)` changes the tree item only. The object passed to `set_data()` is not modified
  and no signal reports the edit.
- `CommandBar` positions its buttons on top of the `QToolBar` layout, because `QToolBar` gives every action button
  exactly its size hint. The overflow menu still decides from the size hints which actions fit.
- `GroupedComboBox` protects headers from popup clicks through an event filter on its view. A view set with
  `setView()` does not get that filter.
- `LabeledSlider` is horizontal only.

## Development

```sh
uv sync --group dev --extra jupyter
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run pyright
uv run pyside-widgets-demo        # widget gallery
```

Tests use `pytest-qt` and run offscreen (`QT_QPA_PLATFORM=offscreen` is set in `tests/conftest.py`). Changes between
versions are listed in [CHANGELOG.md](CHANGELOG.md).
