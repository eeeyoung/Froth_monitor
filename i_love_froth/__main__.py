"""The entry point for the Bubble Analyser program."""

from i_love_froth.gui import MainGUI
# from .gui import MainGUI
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
                                QMenuBar, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                                QComboBox, QMessageBox, QDialog, QLineEdit)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())