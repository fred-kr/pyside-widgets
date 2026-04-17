from pyside_widgets.plugins.plugin_base import PluginBase


class ContainerPlugin(PluginBase):
    def group(self) -> str:
        return super().group() + " (Container)"

    def isContainer(self) -> bool:
        return True
