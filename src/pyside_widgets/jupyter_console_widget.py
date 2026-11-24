from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import QSignalBlocker, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

try:
    from qtconsole import inprocess
except ImportError as exc:
    raise ImportError(
        "JupyterConsoleWindow requires the 'jupyter' extra: pip install 'pyside-widgets[jupyter]'"
    ) from exc

if TYPE_CHECKING:
    import jupyter_client

type ConsoleStyle = Literal["lightbg", "linux", "nocolor"]


class JupyterConsoleWidget(inprocess.QtInProcessRichJupyterWidget, QWidget):
    """
    Rich Jupyter console backed by an in-process kernel that shuts down with the application.

    ``QWidget`` is listed again as a base only so type checkers see it: qtconsole ships no type information.
    """

    def __init__(self, parent: QWidget | None = None, *, style: ConsoleStyle = "linux") -> None:
        super().__init__(parent)
        self.set_default_style(style)

        self.kernel_manager: inprocess.QtInProcessKernelManager = inprocess.QtInProcessKernelManager()
        self.kernel_manager.start_kernel()

        self.kernel_client: jupyter_client.blocking.client.BlockingKernelClient = self.kernel_manager.client()
        self.kernel_client.start_channels()

        app_inst = QApplication.instance()
        if app_inst is not None:
            app_inst.aboutToQuit.connect(self.shutdown_kernel)

    @Slot()
    def shutdown_kernel(self) -> None:
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()


class JupyterConsoleWindow(QWidget):
    """Window around ``JupyterConsoleWidget`` with a checkable ``toggle_view_action`` for a View menu."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        namespace: dict[str, Any] | None = None,
        style: ConsoleStyle = "linux",
    ) -> None:
        """
        Args:
            parent: Parent widget.
            namespace: Variables made available in the console.
            style: Color scheme of the console.
        """
        super().__init__(parent)

        self.toggle_view_action = QAction(self.tr("Toggle Jupyter Console"), self)
        self.toggle_view_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.Computer))
        self.toggle_view_action.setCheckable(True)
        self.toggle_view_action.toggled.connect(self.setVisible)

        self.console = JupyterConsoleWidget(self, style=style)
        layout = QVBoxLayout(self)
        layout.addWidget(self.console)

        self.setWindowTitle(self.tr("Jupyter Console"))
        self.resize(900, 600)

        self._push_namespace(namespace or {})

    def _push_namespace(self, namespace: dict[str, Any]) -> None:
        kernel = self.console.kernel_manager.kernel
        if kernel is None or kernel.shell is None:
            return
        kernel.shell.push(namespace)
        self.console.execute("whos")

    def closeEvent(self, event: QCloseEvent) -> None:
        with QSignalBlocker(self.toggle_view_action):
            self.toggle_view_action.setChecked(False)
        super().closeEvent(event)

    def setVisible(self, visible: bool) -> None:
        with QSignalBlocker(self.toggle_view_action):
            self.toggle_view_action.setChecked(visible)
        super().setVisible(visible)
