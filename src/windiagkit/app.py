from .config import load_settings
from .console_utils import pause
from .menus import main_menu


def main():
    warnings = []
    settings = load_settings(warn=warnings.append)
    if warnings:
        print("\n".join(warnings))
        pause("Press Enter to continue with validated settings...")
    main_menu(settings)
