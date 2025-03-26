"""The entry point for the Bubble Analyser program."""

from froth_monitor.gui import MainGUI
# from .gui import MainGUI
from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())