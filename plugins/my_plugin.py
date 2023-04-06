# my_plugin.py

from plugin_interface import PluginInterface

class Plugin(PluginInterface):
    def __init__(self, config):
        super().__init__(config)

    def execute(self):
        # Implementer plugin-logikken her
        print("MyPlugin is running")
