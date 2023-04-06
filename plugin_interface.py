# plugin_interface.py

from abc import ABC, abstractmethod

class PluginInterface(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def execute(self):
        pass
