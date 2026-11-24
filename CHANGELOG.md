# Changelog

This file lists what changed between releases of pyside-widgets, for developers who upgrade an application that uses
the package. Each release names the breaking changes first, with the replacement for every removed name.

## 0.5.0 (2026-11-24)

Verified with PySide6 6.12.0 on Python 3.14.

### Breaking changes

| Before | After |
|---|---|
| `SettingCard("Title", widget, ...)` with positional arguments | `SettingCard(parent, title="Title", editor_widget=widget)`. Only `parent` is positional. |
| `SettingCard(default_value=..., set_value_name=...)` | Removed. Connect `sig_reset_clicked` and reset the editor yourself. |
| `ColorPickerButton.color()` | `get_color()`, or the property `button.color` (no call). |
| `EnumComboBox.current_enum()` | `get_current_enum()`. The old name still works and emits `DeprecationWarning`. It is removed in 0.6. |
| `EnumComboBox.set_current_enum(member)` ignored a member that is not in the box | Raises `ValueError`. |
| `ResizableMessageBox.question()`, `information()`, `warning()`, `critical()`, `from_exception()` returned `int` | Return `QMessageBox.StandardButton`. `clicked_button()` returns the same type. |
| `ResizableMessageBox.Icon` was an `IntEnum` of the package; `set_icon()` accepted `int` | `ResizableMessageBox.Icon` is `QMessageBox.Icon`. `set_icon()` takes a member of it. |
| Qt properties `icon`, `text`, `detail_text` on `ResizableMessageBox` | Removed. Use `get_icon()`/`set_icon()` and the matching methods. |
| Qt properties `reset_shown`, `icon_size` (`SettingCard`), `bg_color`, `bar_color` (`OverlayWidget`), `stroke_width` (`IndeterminateSpinner`), `handle_position`, `pulse_radius` (`ToggleSwitch`) | `resetShown`, `iconSize`, `bgColor`, `barColor`, `strokeWidth`, `handlePosition`, `pulseRadius`. Update `.ui` files and `setProperty()` calls. The `get_x()`/`set_x()` methods are unchanged. |
| `GroupedComboBox.currentData(role)` ignored `role` and returned `None` for rows added with `addItem()` | Behaves as `QComboBox.currentData(role)`. |
| `LabeledSlider.orientation()`, `setOrientation()` | Removed. The slider is horizontal only. |
| `IndeterminateSpinner` derived from `QProgressBar` and spun while hidden | Derives from `QWidget` and spins only while visible. |
| Options such as `ColorPickerButton(parent, color)` passed positionally | Every constructor parameter after `parent` is keyword-only. `ResizableMessageBox` keeps the positional order of `QMessageBox`. |
| Commands `demo` and `designer` | `pyside-widgets-demo` and `pyside-widgets-designer`. |
| Designer entries for `ResizableMessageBox` and `OverlayWidget` | Removed. Create both in code. |
| Modules `plugins.plugin_base`, `plugins.input_plugin`, `plugins.composite_plugin`, `plugins.container_plugin`, `plugins.toolbar_plugin`, `_style_sheets` | Removed. `plugins.register_widgets` holds one table, `DESIGNER_WIDGETS`. |

### Fixed

- **Designer properties work in `pyside6-uic` output.** uic writes a property `fooBar` as `setFooBar(value)`. Only
  `EnumComboBox.setAllowNone` existed, so a form that set, for example, `fill` on a `CommandBar` raised
  `AttributeError: 'CommandBar' object has no attribute 'setFill'` when the generated code ran. Every designable
  property now has that setter.
- **`SettingCard` and `ResizableMessageBox` crashed when created as `Widget(parent)`**, which is how Designer and uic
  create widgets. `SettingCard` now takes `parent` first.
- **`pyside-widgets-designer` loads the plugins from an editable install.** Designer's interpreter ignores `.pth`
  files and failed with `ModuleNotFoundError: No module named 'pyside_widgets'`. The launcher now sets `PYTHONPATH`,
  keeps an existing `PYSIDE_DESIGNER_PLUGINS`, and starts the `pyside6-designer` of the running environment.
- `DecimalSpinBox` reported a size hint wide enough for the arrow buttons only (36 px where `QDoubleSpinBox` with the
  same range reports 228 px). It now measures its minimum and maximum text.
- `DecimalSpinBox` kept out-of-range text on screen after Return or focus loss (`150` displayed, value `100.00`). The
  text is now normalized. `setSingleStep()` raises `ValueError` for a step that is not greater than zero.
- `DataTreeWidget.filter_tree()` hid a matching item whose parent did not match. Ancestors and the subtree of a match
  now stay visible. The context menu opened offset by the header height.
- `GroupedComboBox`: the first header became the current item, arrow keys and the wheel stopped on headers, and a
  click on a separator selected the last hovered item. Headers and separators can no longer become current.
- `EnumComboBox.sig_current_enum_changed` fired up to three times, twice with `None`, when the rows were rebuilt. It
  now fires once, and only when the member changed.
- `CommandBar` lost its fill or alignment geometry after any toolbar layout pass, for example a changed action text,
  until the next resize.
- `SettingCard` restyled every `QLabel` inside its editor widget (`Segoe UI`, 14 px) through a style sheet. The card
  no longer sets one. Its fonts scale with the application font, and its height follows its content instead of being
  fixed at 50 or 70 px.
- `OverlayWidget.hide_overlay()` enabled a parent that was disabled before the overlay was shown, and `show()` did
  not cover or disable the parent. `show()`, `setVisible()` and `show_overlay()` are now equivalent and the previous
  enabled state is restored.
- `ColorPickerButton(color=QColor())` had no color, icon or text. An invalid color now selects the accent color.
- `ToggleSwitch` looked the same disabled and enabled, and showed no keyboard focus.

### Added

- USER properties with change signals: `ColorPickerButton.color`, `EnumComboBox.currentEnum`,
  `DecimalSpinBox.decimalValue`, `LabeledSlider.sliderValue`. Item delegates and `QDataWidgetMapper` can now edit
  through these widgets.
- `SettingCard.set_editor_widget()`, `LabeledSlider.title`, `EnumComboBox.set_current_enum()` accepts the plain value
  of a member.
- `IndeterminateSpinner` and `ValueSlider` are exported from the package root.
- Designer entries for `AnimatedToggleSwitch`, `LabeledSlider`, `GroupedComboBox`, `DataTreeWidget` and
  `SearchableDataTreeWidget`.
- User-visible strings go through `tr()`.
