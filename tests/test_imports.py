"""Import hygiene: the package must not drag optional or heavy modules in on import."""

import importlib.util
import subprocess
import sys

import pytest

_CHECK = """
import sys
import pyside_widgets
for name in ("qtconsole", "IPython", "numpy", "pyqtgraph", "PySide6.QtDesigner"):
    assert name not in sys.modules, f"{name} was imported by 'import pyside_widgets'"
print("ok")
"""


def test_import_does_not_load_optional_modules():
    # A subprocess keeps pytest-qt and other test-time imports out of sys.modules.
    result = subprocess.run([sys.executable, "-c", _CHECK], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


@pytest.mark.skipif(importlib.util.find_spec("qtconsole") is None, reason="qtconsole not installed")
def test_jupyter_console_is_available_lazily():
    import pyside_widgets

    assert "JupyterConsoleWindow" in dir(pyside_widgets)
    from pyside_widgets import JupyterConsoleWindow  # noqa: F401  (lazy attribute resolves)


def test_unknown_attribute_raises_attribute_error():
    import pyside_widgets

    with pytest.raises(AttributeError):
        pyside_widgets.DoesNotExist  # noqa: B018
