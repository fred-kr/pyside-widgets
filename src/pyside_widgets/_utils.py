import enum

import darkdetect


class Theme(enum.Enum):
    LIGHT = "Light"
    DARK = "Dark"
    AUTO = "Auto"


def is_dark_theme() -> bool:
    t = darkdetect.theme()
    t = Theme(t) if t else Theme.LIGHT
    return t == Theme.DARK
