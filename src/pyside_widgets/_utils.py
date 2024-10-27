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


class _Nothing(enum.Enum):
    NOTHING = enum.auto()

    def __repr__(self) -> str:
        return "NOTHING"

    def __bool__(self) -> bool:
        return False


NOTHING = _Nothing.NOTHING
