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