"""Object-oriented configuration loading boundary."""

from .config import _load_settings


class ConfigurationLoader:
    def __init__(self, path=None, warn=print):
        self.path = path
        self.warn = warn

    def load(self):
        return _load_settings(path=self.path, warn=self.warn)
