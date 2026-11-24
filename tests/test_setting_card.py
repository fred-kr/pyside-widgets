import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QTextEdit, QWidget

from pyside_widgets import SettingCard
from pyside_widgets._icons import get_icon


@pytest.fixture
def card(qtbot) -> SettingCard:
    widget = SettingCard(title="Sampling rate", description="Samples per second", editor_widget=QSpinBox())
    qtbot.addWidget(widget)
    return widget


def test_parent_is_the_only_positional_argument(qtbot):
    """pyside6-uic and Designer create every widget as ``Widget(parent)``."""
    host = QWidget()
    qtbot.addWidget(host)
    card = SettingCard(host)
    assert card.parent() is host
    assert card.get_title() == ""
    assert card.editor_widget is None
    with pytest.raises(TypeError):
        SettingCard(host, "Title")  # pyright: ignore[reportCallIssue]


def test_text_properties(card: SettingCard):
    assert card.get_title() == "Sampling rate"
    assert card.get_description() == "Samples per second"
    card.setProperty("title", "Rate")
    card.setProperty("description", "")
    assert card.get_title() == "Rate"
    assert not card._description_label.isVisibleTo(card)
    card.set_description("Hz")
    assert card._description_label.isVisibleTo(card)


def test_reset_button_emits_and_can_be_hidden(qtbot, card: SettingCard):
    with qtbot.waitSignal(card.sig_reset_clicked):
        card.btn_reset.click()
    assert card.get_reset_shown() is True
    card.setProperty("resetShown", False)
    assert card.get_reset_shown() is False
    assert not card.btn_reset.isVisibleTo(card)


def test_icon_and_icon_size(card: SettingCard):
    assert card.get_icon().isNull()
    assert not card._icon_label.isVisibleTo(card)
    card.set_icon(get_icon("Settings"))
    assert card._icon_label.isVisibleTo(card)
    card.setProperty("iconSize", QSize(24, 24))
    assert card.get_icon_size() == QSize(24, 24)


def test_set_editor_widget_replaces_the_editor(card: SettingCard):
    first = card.editor_widget
    replacement = QSpinBox()
    card.set_editor_widget(replacement)
    assert card.editor_widget is replacement
    assert replacement.parent() is card
    assert first is not None and first.parent() is None

    card.set_editor_widget(None)
    assert card.editor_widget is None
    assert replacement.parent() is None


def test_card_does_not_restyle_widgets_inside_the_editor(qtbot):
    """A style sheet on the card would cascade into every QLabel below it; the card must not set one."""
    reference = QLabel("reference")
    qtbot.addWidget(reference)

    editor = QWidget()
    inner = QLabel("inner", editor)
    QHBoxLayout(editor).addWidget(inner)
    card = SettingCard(title="Title", editor_widget=editor)
    qtbot.addWidget(card)
    card.show()

    assert card.styleSheet() == ""
    assert inner.font().family() == reference.font().family()
    assert inner.font().pointSizeF() == reference.font().pointSizeF()
    assert inner.font().pixelSize() == reference.font().pixelSize()


def test_fonts_follow_the_card_font(card: SettingCard):
    base = card.font().pointSizeF()
    assert card._title_label.font().pointSizeF() > base > card._description_label.font().pointSizeF()

    bigger = QFont(card.font())
    bigger.setPointSizeF(base * 2)
    card.setFont(bigger)
    assert card._title_label.font().pointSizeF() == pytest.approx(base * 2 * 1.15)
    assert card._description_label.font().pointSizeF() == pytest.approx(base * 2 * 0.9)


def test_height_grows_with_the_content(qtbot):
    """The card used to be fixed at 50 or 70 px and clipped anything taller."""
    small = SettingCard(title="Title", editor_widget=QSpinBox())
    with_description = SettingCard(title="Title", description="Description", editor_widget=QSpinBox())
    tall_editor = QTextEdit()
    tall_editor.setFixedHeight(200)
    tall = SettingCard(title="Title", editor_widget=tall_editor)
    for widget in (small, with_description, tall):
        qtbot.addWidget(widget)

    assert with_description.sizeHint().height() > small.sizeHint().height()
    assert tall.sizeHint().height() >= 200
    assert small.maximumHeight() > 1000  # no fixed height
