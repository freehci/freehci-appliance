# plugins/my_plugin.py

from plugin_interface import PluginInterface

class Plugin(PluginInterface):
    def __init__(self, config):
        super().__init__(config)

    def execute(self):
        # Implement plugin logic here
        print("MyPlugin is running")
