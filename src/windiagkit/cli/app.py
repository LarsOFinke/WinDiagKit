from ..configuration_loader import ConfigurationLoader
from .console import pause
from .menus import main_menu


def main():
    warnings = []
    settings = ConfigurationLoader(warn=warnings.append).load()
    if warnings:
        print("\n".join(warnings))
        pause("Press Enter to continue with validated settings...")
    main_menu(settings)
