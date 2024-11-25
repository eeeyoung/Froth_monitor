<<<<<<< HEAD
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QFont

app = QApplication([])

# Main Window
window = QWidget()
window.setWindowTitle("QLabel Font Example")
layout = QVBoxLayout(window)

# Styled QLabel
label = QLabel("Styled Text")
font = QFont("Helvetica", 18, QFont.Bold)
font.setItalic(True)
label.setFont(font)
layout.addWidget(label)

# Show Window
window.show()
app.exec()
=======
from PySide6.QtWidgets import (QApplication, QProgressDialog)

        

QApplication()
"""Create and show a progress window with a loading bar."""
calculation_progress_dialog = QProgressDialog("Working...",  "Calculating FPS...")
calculation_progress_dialog.setWindowTitle("Working...")


# layout = QVBoxLayout(self.calculation_progress_dialog)

# self.progress_label = QLabel("Calculating FPS...", self.calculation_progress_dialog)
# self.progress_label.setText("Calculating FPS...")
# self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
# self.progress_label.setStyleSheet("background-color: none; color: black;")


# layout.addWidget(self.progress_label)

# self.calculation_progress_dialog.setLayout(layout)
calculation_progress_dialog.show()
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
