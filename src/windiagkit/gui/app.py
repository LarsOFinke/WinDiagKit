import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from .. import __version__
from ..cli.console import APP_NAME
from ..config import load_settings
from .window import MainWindow


def main():
    smoke_test = "--smoke-test" in sys.argv
    qt_arguments = [argument for argument in sys.argv if argument != "--smoke-test"]
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    application = QApplication(qt_arguments)
    application.setStyle("Fusion")
    application.setApplicationName(APP_NAME)
    application.setApplicationVersion(__version__)

    warnings = []
    settings = load_settings(warn=warnings.append)
    window = MainWindow(settings)
    window.show()

    if warnings:
        QMessageBox.warning(window, "Configuration warnings", "\n".join(warnings))
    if smoke_test:
        QTimer.singleShot(250, application.quit)
    return application.exec_()
