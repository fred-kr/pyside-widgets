"""Bundled icons are black on light palettes, white on dark palettes, and follow a palette switch."""

import gc

import pytest
from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QColor, QIcon, QImage, QPalette, QPixmap, QRegion
from PySide6.QtWidgets import QApplication, QWidget

from pyside_widgets import SettingCard
from pyside_widgets._icons import get_icon

ICON_NAMES = ["ArrowReset", "MoreHorizontal", "Settings"]


@pytest.fixture
def set_scheme(qapp):
    """Switches the application palette between a light and a dark window color; restores it afterwards."""
    original = QApplication.palette()

    def _set(dark: bool) -> None:
        palette = QPalette(original)
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30) if dark else QColor(240, 240, 240))
        QApplication.setPalette(palette)

    yield _set
    QApplication.setPalette(original)


def _lightness_of_opaque_pixels(source: QPixmap | QImage) -> set[int]:
    image = source.toImage() if isinstance(source, QPixmap) else source
    pixels = [image.pixelColor(x, y) for x in range(image.width()) for y in range(image.height())]
    return {color.lightness() for color in pixels if color.alpha() == 255}


@pytest.mark.parametrize("name", ICON_NAMES)
def test_icon_follows_the_palette(set_scheme, name):
    icon = get_icon(name)
    assert not icon.isNull()

    set_scheme(dark=False)
    light = _lightness_of_opaque_pixels(icon.pixmap(QSize(32, 32)))
    assert light and max(light) < 64

    set_scheme(dark=True)
    assert _lightness_of_opaque_pixels(icon.pixmap(QSize(32, 32))) == {255}


def test_dark_icon_keeps_shape_and_device_pixel_ratio(set_scheme):
    icon = get_icon("Settings")
    set_scheme(dark=False)
    light = icon.pixmap(QSize(16, 16), 2.0)
    set_scheme(dark=True)
    dark = icon.pixmap(QSize(16, 16), 2.0)

    assert dark.size() == light.size() == QSize(32, 32)
    assert dark.devicePixelRatio() == 2.0
    assert dark.toImage().convertToFormat(QImage.Format.Format_Alpha8) == light.toImage().convertToFormat(
        QImage.Format.Format_Alpha8
    )


def test_disabled_dark_icon_differs_from_normal(set_scheme):
    set_scheme(dark=True)
    icon = get_icon("ArrowReset")
    normal = icon.pixmap(QSize(32, 32), 1.0, QIcon.Mode.Normal).toImage()
    disabled = icon.pixmap(QSize(32, 32), 1.0, QIcon.Mode.Disabled).toImage()
    assert normal != disabled


def test_detached_copy_still_renders(set_scheme):
    set_scheme(dark=True)
    copy = QIcon(get_icon("ArrowReset"))
    copy.setIsMask(True)  # modifying a shared icon makes Qt clone the engine
    gc.collect()
    assert _lightness_of_opaque_pixels(copy.pixmap(QSize(32, 32))) == {255}


def test_setting_card_icon_repaints_after_palette_switch(qtbot, set_scheme):
    set_scheme(dark=False)
    card = SettingCard(title="Sampling rate", icon=get_icon("Settings"))
    card.set_icon_size(QSize(32, 32))
    qtbot.addWidget(card)
    card.show()

    label = card._icon_label
    assert max(_lightness_of_opaque_pixels(_icon_only(label))) < 64

    set_scheme(dark=True)
    assert _lightness_of_opaque_pixels(_icon_only(label)) == {255}


def test_setting_card_palette_follows_application_palette(qtbot, set_scheme):
    set_scheme(dark=False)
    card = SettingCard(title="Sampling rate")
    qtbot.addWidget(card)
    card.show()

    set_scheme(dark=True)
    assert card.palette().color(QPalette.ColorRole.Window) == QColor(30, 30, 30)
    assert card.btn_reset.palette().color(QPalette.ColorRole.Window) == QColor(30, 30, 30)


def _icon_only(label: QWidget) -> QImage:
    """Render the icon label on a transparent background, without its parent."""
    image = QImage(label.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    label.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)  # no window background
    return image
