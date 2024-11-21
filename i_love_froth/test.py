from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
                                QMenuBar, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                                QComboBox, QMessageBox, QDialog, QLineEdit)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QImage
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
import sys
import cv2
import numpy as np
from datetime import datetime
from image_analysis import VideoAnalysisModule

class ROI:
    def __init__(self, rect: QRect):
        self.rect = rect
        self.analysis_module = VideoAnalysisModule()

class MainGUI(QMainWindow):
    def __init__(self):
        super(MainGUI, self).__init__()
        self.setWindowTitle('I love Froths')
        self.setGeometry(100, 100, 1200, 600)
        
        # Video-related attributes
        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.playing = False
        
        # ROI and Video Analysis
        self.rois = []  # List of ROI instances
        self.current_roi_start = None  # Starting point of the currently drawn ROI
        self.current_roi_rect = None  # QRect of the ROI being drawn
        self.drawing_roi = False  # Flag for ROI drawing
        self.current_pixmap = None  # Store the current video frame as QPixmap for real-time updates
        
        # Define UI elements
        self.initUI()

    def initUI(self):
        
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Menu bar
        self.createMenuBar()

        # Grid layout for buttons and canvas
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        # Buttons
        self.add_buttons(grid_layout)

        # Video canvas placeholder
        self.add_canvas_placeholder(grid_layout)

        # Overflow direction label
        self.add_overflow_direction_label(grid_layout)

        # Overflow direction value label
        self.direction_label = QLabel("-0.5 * Pi degree", self)
        self.direction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.direction_label, 3, 1)

    def createMenuBar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # File menu
        file_menu = QMenu("Import", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction("Import Local Video", self.import_local_video)
        file_menu.addAction("Load Camera", self.load_camera_dialog)

        # Export menu
        export_menu = QMenu("Export", self)
        menu_bar.addMenu(export_menu)
        export_menu.addAction("Export Settings", self.export_setting_window)

    def add_buttons(self, layout):
        self.add_roi_button = QPushButton("Add One ROI", self)
        self.add_roi_button.clicked.connect(self.start_drawing_roi)
        layout.addWidget(self.add_roi_button, 1, 0, 1, 2)

        self.pause_play_button = QPushButton("Pause/Play", self)
        self.pause_play_button.clicked.connect(self.pause_play)
        layout.addWidget(self.pause_play_button, 2, 0, 1, 2)

        self.save_end_button = QPushButton("Save and End Playing", self)
        self.save_end_button.clicked.connect(self.excel_file_output)
        layout.addWidget(self.save_end_button, 4, 0, 1, 2)

    def add_canvas_placeholder(self, layout):
        
        self.video_canvas_label = QLabel("Video Canvas", self)
        self.video_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_canvas_label.setStyleSheet("background-color: green;")
        self.video_canvas_label.setFixedSize(700, 400)
        layout.addWidget(self.video_canvas_label, 0, 2, 8, 6)

        # Mouse events for ROI drawing
        self.video_canvas_label.mousePressEvent = self.mouse_press_event
        self.video_canvas_label.mouseMoveEvent = self.mouse_move_event
        self.video_canvas_label.mouseReleaseEvent = self.mouse_release_event
        
    def add_overflow_direction_label(self, layout):
        
        self.overflow_label = QLabel("Overflow\nDirection:", self)
        self.overflow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.overflow_label, 3, 0)

    def import_local_video(self):
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            self.video_capture = cv2.VideoCapture(file_path)
            if not self.video_capture.isOpened():
                QMessageBox.critical(self, "Error", "Could not open the video file!")
            else:
                self.playing = True
                self.timer.start(30)

    def load_camera_dialog(self):
        # Implementation similar to original code
        pass

    def pause_play(self):
        
        if self.video_capture is None or not self.video_capture.isOpened():
            QMessageBox.warning(self, "No Video/Camera", "Please load a video or camera first!")
            return

        self.playing = not self.playing
        if self.playing:
            self.timer.start(30)
        else:
            self.timer.stop()

    def display_frame(self):
        
        if self.video_capture is not None and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if not ret:
                self.timer.stop()
                return

            # Draw ROIs on the frame
            for roi in self.rois:
                x, y, w, h = roi.rect.x(), roi.rect.y(), roi.rect.width(), roi.rect.height()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Update VideoAnalysisModules for each ROI
            for roi in self.rois:
                x, y, w, h = roi.rect.x(), roi.rect.y(), roi.rect.width(), roi.rect.height()
                roi_frame = frame[y:y+h, x:x+w]
                roi.analysis_module.analyze(roi_frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            q_img = QImage(frame.data, width, height, channel * width, QImage.Format_RGB888)
            self.current_pixmap = QPixmap.fromImage(q_img)
            self.video_canvas_label.setPixmap(self.current_pixmap)

    def start_drawing_roi(self):
        self.drawing_roi = True

    def mouse_press_event(self, event):
        if self.drawing_roi:
            # Adjust the start position based on scaling and offsets
            self.current_roi_start = self.adjust_mouse_position(event.pos())

    def mouse_move_event(self, event):
        if self.drawing_roi and self.current_roi_start:
            # Adjust the current position while dragging
            end = self.adjust_mouse_position(event.pos())
            start = self.current_roi_start
            self.current_roi_rect = QRect(start, end)
            self.update_video_with_roi()

    def mouse_release_event(self, event):
        if self.drawing_roi:
            # Adjust the end position
            end = self.adjust_mouse_position(event.pos())
            start = self.current_roi_start
            self.current_roi_rect = QRect(start, end)
            if self.current_roi_rect.width() > 0 and self.current_roi_rect.height() > 0:
                new_roi = ROI(self.current_roi_rect)
                self.rois.append(new_roi)
                QMessageBox.information(self, "ROI Added", f"ROI #{len(self.rois)} added.")
            else:
                QMessageBox.warning(self, "Invalid ROI", "The drawn ROI is invalid.")
            self.drawing_roi = False
            self.current_roi_start = None
            self.current_roi_rect = None
            self.update()

    def adjust_mouse_position(self, pos):
        """
        Adjust the mouse position relative to the displayed video frame.
        """
        if not self.current_pixmap:
            return pos

        # Get the QLabel and pixmap sizes
        label_width = self.video_canvas_label.width()
        label_height = self.video_canvas_label.height()
        pixmap_width = self.current_pixmap.width()
        pixmap_height = self.current_pixmap.height()

        print(label_height,
              label_width,
              pixmap_height,
              pixmap_width)
        
        diff_height = pixmap_height - label_height
        diff_width = pixmap_width - label_width

        # Adjust for scaling
        adjusted_x = int(pos.x() + diff_width/2)
        adjusted_y = int(pos.y() + diff_height/2) 

        # Ensure coordinates are within the pixmap bounds
        # adjusted_x = min(max(adjusted_x, 0), pixmap_width - 1)
        # adjusted_y = min(max(adjusted_y, 0), pixmap_height - 1)

        return QPoint(adjusted_x, adjusted_y)
    
    def update_video_with_roi(self):
        # Overlay the drawing ROI on the current video frame
        if self.current_pixmap and self.current_roi_rect:
            temp_pixmap = self.current_pixmap.copy()
            painter = QPainter(temp_pixmap)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.current_roi_rect)
            painter.end()
            self.video_canvas_label.setPixmap(temp_pixmap)


    def export_setting_window(self):
        # Implementation similar to original code
        pass

    def excel_file_output(self):
        # Export logic here
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
