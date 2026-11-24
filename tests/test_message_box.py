import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMessageBox

from pyside_widgets.message_box import ResizableMessageBox

Ok = QMessageBox.StandardButton.Ok
Cancel = QMessageBox.StandardButton.Cancel
Yes = QMessageBox.StandardButton.Yes
NoButton = QMessageBox.StandardButton.NoButton


@pytest.fixture
def dialog(qtbot) -> ResizableMessageBox:
    widget = ResizableMessageBox(
        icon=QMessageBox.Icon.Warning,
        title="Title",
        text="Body",
        buttons=Ok | Cancel,
        default_button=Cancel,
    )
    qtbot.addWidget(widget)
    return widget


def _click_when_open(button: QDialogButtonBox.StandardButton) -> None:
    """Click ``button`` in the ResizableMessageBox that a following modal ``exec()`` opens."""

    def click() -> None:
        box = QApplication.activeModalWidget()
        assert isinstance(box, ResizableMessageBox)
        box.button_box().button(button).click()

    QTimer.singleShot(0, click)


def test_clicked_button_and_result(dialog: ResizableMessageBox):
    assert dialog.clicked_button() is None
    dialog.button_box().button(QDialogButtonBox.StandardButton.Ok).click()
    assert dialog.clicked_button() == Ok
    assert dialog.result() == Ok.value


def test_default_button(dialog: ResizableMessageBox):
    assert dialog.button_box().button(QDialogButtonBox.StandardButton.Cancel).isDefault()


def test_escape_maps_to_cancel(dialog: ResizableMessageBox):
    dialog.reject()
    assert dialog.clicked_button() == Cancel
    assert dialog.result() == Cancel.value


def test_escape_without_cancel_maps_to_no_button(qtbot):
    widget = ResizableMessageBox(buttons=Ok)
    qtbot.addWidget(widget)
    widget.reject()
    assert widget.clicked_button() == NoButton
    assert widget.result() == 0


def test_static_helper_returns_a_qmessagebox_standard_button(qtbot):
    """``StandardButton`` is an ``enum.Flag``: an int never equals a member, so the helpers return the member."""
    _click_when_open(QDialogButtonBox.StandardButton.Yes)
    answer = ResizableMessageBox.question(None, "Save", "Save changes?")
    assert answer == Yes
    assert isinstance(answer, QMessageBox.StandardButton)


def test_dialog_button_box_buttons_are_accepted(qtbot):
    widget = ResizableMessageBox(
        buttons=QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
        default_button=QDialogButtonBox.StandardButton.No,
    )
    qtbot.addWidget(widget)
    widget.button_box().button(QDialogButtonBox.StandardButton.Yes).click()
    assert widget.clicked_button() == Yes


def test_icon_round_trip(dialog: ResizableMessageBox):
    assert ResizableMessageBox.Icon is QMessageBox.Icon
    assert dialog.get_icon() == QMessageBox.Icon.Warning
    dialog.set_icon(QMessageBox.Icon.Critical)
    assert dialog.get_icon() == QMessageBox.Icon.Critical
    assert dialog._icon_label.isVisibleTo(dialog)
    assert not dialog._icon_label.pixmap().isNull()
    dialog.set_icon(QMessageBox.Icon.NoIcon)
    assert not dialog._icon_label.isVisibleTo(dialog)


def test_detail_toggle_visibility(dialog: ResizableMessageBox):
    assert not dialog._detail_toggle.isVisibleTo(dialog)
    dialog.set_detail_text("trace")
    assert dialog._detail_toggle.isVisibleTo(dialog)
    assert dialog.get_detail_text() == "trace"
    dialog.set_detail_text("")
    assert not dialog._detail_toggle.isVisibleTo(dialog)


def test_detail_section_uses_a_fixed_pitch_font_and_no_style_sheet(dialog: ResizableMessageBox):
    assert dialog._detail_widget.styleSheet() == ""
    assert dialog._detail_widget.font().styleHint() in (
        dialog._detail_widget.font().StyleHint.Monospace,
        dialog._detail_widget.font().StyleHint.TypeWriter,
        dialog._detail_widget.font().StyleHint.AnyStyle,
    )


def test_set_exception_formats_traceback(dialog: ResizableMessageBox):
    try:
        raise ValueError("boom")
    except ValueError as exc:
        dialog.set_exception(exc)
    assert "ValueError: boom" in dialog.get_detail_text()
    assert "Traceback" in dialog.get_detail_text()


def test_detail_button_has_icon(dialog: ResizableMessageBox):
    assert not dialog._detail_toggle.icon().isNull()
