from typing import TYPE_CHECKING, Any, Literal

from PySide6 import QtCore, QtGui, QtWidgets

try:
    from qtconsole import inprocess
except ImportError as exc:
    raise ImportError(
        "JupyterConsoleWindow requires the 'jupyter' extra: pip install 'pyside-widgets[jupyter]'"
    ) from exc

if TYPE_CHECKING:
    import jupyter_client

type ConsoleStyle = Literal["lightbg", "linux", "nocolor"]


class JupyterConsoleWidget(inprocess.QtInProcessRichJupyterWidget, QtWidgets.QWidget):
    """
    Rich Jupyter console backed by an in-process kernel that shuts down with the application.

    ``QWidget`` is listed again as a base only so type checkers see it: qtconsole ships no type information.
    """

    def __init__(self, style: ConsoleStyle = "linux") -> None:
        super().__init__()
        self.set_default_style(style)

        self.kernel_manager: inprocess.QtInProcessKernelManager = inprocess.QtInProcessKernelManager()
        self.kernel_manager.start_kernel()

        self.kernel_client: jupyter_client.blocking.client.BlockingKernelClient = self.kernel_manager.client()
        self.kernel_client.start_channels()

        app_inst = QtWidgets.QApplication.instance()
        if app_inst is not None:
            app_inst.aboutToQuit.connect(self.shutdown_kernel)

    @QtCore.Slot()
    def shutdown_kernel(self) -> None:
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()


class JupyterConsoleWindow(QtWidgets.QWidget):
    """Top-level window around ``JupyterConsoleWidget`` with a checkable ``toggle_view_action`` for a View menu."""

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        namespace: dict[str, Any] | None = None,
        style: ConsoleStyle = "linux",
    ) -> None:
        super().__init__(parent)

        self.toggle_view_action = QtGui.QAction("Toggle Jupyter Console", self)
        self.toggle_view_action.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.Computer))
        self.toggle_view_action.setCheckable(True)
        self.toggle_view_action.toggled.connect(self.setVisible)

        self.console = JupyterConsoleWidget(style=style)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.console)

        self.setWindowTitle("Jupyter Console")
        self.resize(900, 600)

        self._push_namespace(namespace or {})

    def _push_namespace(self, namespace: dict[str, Any]) -> None:
        kernel = self.console.kernel_manager.kernel
        if kernel is None or kernel.shell is None:
            return
        kernel.shell.push(namespace)
        self.console.execute("whos")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        with QtCore.QSignalBlocker(self.toggle_view_action):
            self.toggle_view_action.setChecked(False)
        super().closeEvent(event)

    def setVisible(self, visible: bool) -> None:
        with QtCore.QSignalBlocker(self.toggle_view_action):
            self.toggle_view_action.setChecked(visible)
        super().setVisible(visible)
