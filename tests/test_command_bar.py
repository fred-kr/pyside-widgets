import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QVBoxLayout, QWidget

from pyside_widgets import CommandBar


@pytest.fixture
def host(qtbot) -> QWidget:
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.resize(600, 200)
    return widget


def _bar_with_actions(host: QWidget, **kwargs) -> tuple[CommandBar, list[QAction]]:
    bar = CommandBar(**kwargs)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(bar)
    actions = [QAction(f"Action {i}", bar) for i in range(3)]
    bar.addActions(actions)
    host.show()
    return bar, actions


def _geometries(bar: CommandBar, actions: list[QAction]) -> list[tuple[int, int]]:
    return [(bar.widgetForAction(a).x(), bar.widgetForAction(a).width()) for a in actions]


def _assert_fills(bar: CommandBar, actions: list[QAction]) -> None:
    geometries = _geometries(bar, actions)
    assert geometries[0][0] == 0
    for (x, width), (next_x, _) in zip(geometries, geometries[1:], strict=False):
        assert x + width == next_x  # no gaps, no overlap
    last_x, last_width = geometries[-1]
    assert last_x + last_width == bar.width()
    widths = [width for _, width in geometries]
    assert max(widths) - min(widths) <= 1


def test_buttons_fill_the_width(qtbot, host):
    bar, actions = _bar_with_actions(host)
    qtbot.waitUntil(lambda: bar.width() == 600)
    _assert_fills(bar, actions)


@pytest.mark.parametrize(
    "change",
    [
        lambda bar, actions: actions[0].setText("A much longer action text"),
        lambda bar, actions: bar.setIconSize(QSize(32, 32)),
        lambda bar, actions: bar.layout().invalidate(),
    ],
    ids=["action text", "icon size", "layout invalidated"],
)
def test_fill_survives_a_toolbar_layout_pass(qtbot, host, change):
    """The toolbar layout resets every button to its size hint; the bar has to re-apply its own geometry after it."""
    bar, actions = _bar_with_actions(host)
    qtbot.waitUntil(lambda: bar.width() == 600)
    change(bar, actions)
    qtbot.wait(50)  # lets the posted LayoutRequest run
    _assert_fills(bar, actions)


def test_align_right_packs_buttons_to_the_right_edge(qtbot, host):
    bar, actions = _bar_with_actions(host, fill=False, alignment=Qt.AlignmentFlag.AlignRight)
    qtbot.waitUntil(lambda: bar.width() == 600)
    last = bar.widgetForAction(actions[-1])
    assert last.x() + last.width() == bar.width()
    assert bar.widgetForAction(actions[0]).x() > 0

    bar.set_alignment(Qt.AlignmentFlag.AlignLeft)
    assert bar.widgetForAction(actions[0]).x() == 0


def test_properties(qtbot, host):
    bar, actions = _bar_with_actions(host)
    assert bar.property("fill") is True
    bar.setProperty("fill", False)
    assert bar.get_fill() is False
    assert bar.widgetForAction(actions[0]).width() == bar.widgetForAction(actions[0]).sizeHint().width()
