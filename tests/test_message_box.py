import pytest
from PySide6.QtWidgets import QDialogButtonBox

from pyside_widgets.message_box import ResizableMessageBox

Ok = QDialogButtonBox.StandardButton.Ok
Cancel = QDialogButtonBox.StandardButton.Cancel
NoButton = QDialogButtonBox.StandardButton.NoButton


@pytest.fixture
def dialog(qtbot) -> ResizableMessageBox:
    widget = ResizableMessageBox(
        icon=ResizableMessageBox.Icon.Warning,
        title="Title",
        text="Body",
        buttons=Ok | Cancel,
        default_button=Cancel,
    )
    qtbot.addWidget(widget)
    return widget


def test_clicked_button_and_result(dialog: ResizableMessageBox):
    assert dialog.clicked_button() is None
    dialog.button_box().button(Ok).click()
    assert dialog.clicked_button() == Ok
    assert dialog.result() == Ok.value


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


def test_icon_property_round_trip(dialog: ResizableMessageBox):
    assert dialog.get_icon() == int(ResizableMessageBox.Icon.Warning)
    assert dialog.property("icon") == int(ResizableMessageBox.Icon.Warning)
    dialog.set_icon(3)
    assert dialog.get_icon() == int(ResizableMessageBox.Icon.Critical)
    assert dialog._icon_label.isVisibleTo(dialog)
    dialog.set_icon(ResizableMessageBox.Icon.NoIcon)
    assert not dialog._icon_label.isVisibleTo(dialog)


def test_detail_toggle_visibility(dialog: ResizableMessageBox):
    assert not dialog._detail_toggle.isVisibleTo(dialog)
    dialog.set_detail_text("trace")
    assert dialog._detail_toggle.isVisibleTo(dialog)
    assert dialog.get_detail_text() == "trace"
    assert dialog.property("detail_text") == "trace"
    dialog.set_detail_text("")
    assert not dialog._detail_toggle.isVisibleTo(dialog)


def test_set_exception_formats_traceback(dialog: ResizableMessageBox):
    try:
        raise ValueError("boom")
    except ValueError as exc:
        dialog.set_exception(exc)
    assert "ValueError: boom" in dialog.get_detail_text()
    assert "Traceback" in dialog.get_detail_text()


def test_detail_button_has_icon(dialog: ResizableMessageBox):
    assert not dialog._detail_toggle.icon().isNull()
