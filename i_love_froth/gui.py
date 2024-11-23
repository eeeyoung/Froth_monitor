from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
                                QMenuBar, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                                QComboBox, QMessageBox, QDialog, QLineEdit)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QImage
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
import pyqtgraph as pg
import sys
import cv2
import csv
import json
import os
import numpy as np
from datetime import datetime
from openpyxl import Workbook
from .arrow import Arrow
from .autosaver import AutoSaver
from .video_recorder import VideoRecorder
from .roi import ROI
from .export import Export
        
class MainGUI(QMainWindow):
    def __init__(self):
        """
        Initializes the main GUI window with essential attributes and UI elements.

        :param self: The main GUI window instance
        :type self: MainGUI
        :return: None
        :rtype: None
        """
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
        
        # Arrow drawing
        self.arrow_angle = np.pi / 2
        self.arrow_locked = False # Lock status for arrow direction
        self.drawing_arrow = False  # Flag to indicate if arrow is being drawn
        self.overflow_direction_label = None  # Label to display the overflow direction angle
        
        # Export setting
        self.export = Export(self)
        
        # Video recording
        self.recording = False
        self.video_writer = None
        
        # Auto Save
        self.auto_saver = AutoSaver()
        self.auto_saver.load_from_file
        
        
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
        # self.add_buttons(grid_layout)

        # Video canvas placeholder
        self.add_canvas_placeholder(grid_layout)

        self.add_arrow_canvas(grid_layout)
        
        # Overflow direction label
        self.add_overflow_direction_label(grid_layout)

        # ROI Movements Canvas
        self.add_ROI_movement_placeholder(grid_layout)
        

        
        # Overflow direction value label
        self.direction_textbox = QLineEdit(self)
        self.direction_textbox.setText(f"{np.degrees(self.arrow_angle):.2f}")  # Default to 90 degrees
        self.direction_textbox.editingFinished.connect(self.manual_arrow_angle_update)
        self.direction_textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.direction_textbox, 1, 1, 1, 1)
        
        self.add_buttons(grid_layout)

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
        export_menu.addAction("Export Settings", self.export.export_setting_window)

    def add_buttons(self, layout):
        self.add_roi_button = QPushButton("Add One ROI", self)
        self.add_roi_button.clicked.connect(self.start_drawing_roi)
        layout.addWidget(self.add_roi_button, 3, 0, 1, 2)

        self.pause_play_button = QPushButton("Pause/Play", self)
        self.pause_play_button.clicked.connect(self.pause_play)
        layout.addWidget(self.pause_play_button, 4, 0, 1, 2)

        self.confirm_arrow_button = QPushButton("Confirm Arrow Direction", self)
        self.confirm_arrow_button.clicked.connect(self.asking_lock_arrow_direction)
        layout.addWidget(self.confirm_arrow_button, 2, 0, 1, 2)
        
        self.save_end_button = QPushButton("Save", self)
        self.save_end_button.clicked.connect(self.save)
        layout.addWidget(self.save_end_button, 5, 0, 1, 2)
        
        self.reset_button = QPushButton("Start a new mission", self)
        self.reset_button.clicked.connect(self.reset_application)
        layout.addWidget(self.reset_button, 6, 0, 1, 2)
        
        self.start_record_button = QPushButton("Start Recording", self)
        self.start_record_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_record_button, 7, 0, 1, 2)

        # self.stop_record_button = QPushButton("Stop Recording", self)
        # self.stop_record_button.clicked.connect(self.stop_recording)
        # layout.addWidget(self.stop_record_button, 9, 0, 1, 2)

    def add_canvas_placeholder(self, layout):
        
        self.video_canvas_label = QLabel("Video Canvas", self)
        self.video_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_canvas_label.setStyleSheet("background-color: none;")
        self.video_canvas_label.setFixedSize(700, 400)
        layout.addWidget(self.video_canvas_label, 0, 2, 8, 6)

        # Mouse events for ROI drawing
        self.video_canvas_label.mousePressEvent = self.mouse_press_event
        self.video_canvas_label.mouseMoveEvent = self.mouse_move_event
        self.video_canvas_label.mouseReleaseEvent = self.mouse_release_event
    
    def add_arrow_canvas(self, layout):
        self.arrow_canvas_label = QLabel("Arrow Display", self)
        self.arrow_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrow_canvas_label.setStyleSheet("background-color: lightgray;")
        self.arrow_canvas_label.setFixedSize(150, 150)
        layout.addWidget(self.arrow_canvas_label, 7, 4, 1, 1)
        
        self.arrow = Arrow(self.arrow_canvas_label)  # Current arrow instance
    
    def add_ROI_movement_placeholder(self, layout):
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setFixedSize(700, 200)
        self.plot_widget.hideAxis('left')  # Hide Y-axis scale
        self.plot_widget.hideAxis('bottom')  # Hide X-axis scale
        self.plot_widget.addLegend()
        layout.addWidget(self.plot_widget, 8, 2, 8, 3)
        
        # Data structure to hold movement curves and buffers
        self.movement_curves = {}  # Store curve references for each ROI
        self.movement_buffers = {}  # Store buffers for each ROI
        self.max_frames = 150  # Maximum number of frames to display
        
    def add_overflow_direction_label(self, layout):
        
        self.add_arrow_button = QPushButton("Add Overflow Arrow")
        self.add_arrow_button.clicked.connect(self.start_drawing_arrow)
        layout.addWidget(self.add_arrow_button, 1, 0, 1, 1)

    def message_boxes(self, event):
        if event == "Confirm Direction":

            reply = QMessageBox.question(
                    self,
                    "Confirm Overflow Direction",
                    f"The current overflow direction is {float(self.direction_textbox.text()):.2f}°.\n"
                    "Would you like to lock this direction?",
                    QMessageBox.Yes | QMessageBox.No,
                )
            if reply == QMessageBox.Yes:
                self.lock_arrow_direction()
            else:
                QMessageBox.warning(self, "Direction Not Confirmed", "Please confirm the arrow direction first.")
                return    
            
        if event == "Arrow Locked":
            QMessageBox.warning(self, "Warning", "Overflow Direction already locked")
            return    
        
    def start_drawing_arrow(self):
        if self.arrow_locked:

            return
        
        self.drawing_arrow = True
        self.direction_textbox.setText("Drawing Overflow Direction...")
        return
    
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
        """
        Opens a dialog to select and load an available camera.
        """
        available_cameras = []
        for index in range(10):  # Check up to 10 camera indices
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                available_cameras.append(f"Camera {index}")
                cap.release()

        if not available_cameras:
            QMessageBox.critical(self, "Error", "No cameras detected!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Camera")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        # Camera selection dropdown
        camera_combo = QComboBox(dialog)
        camera_combo.addItems(available_cameras)
        layout.addWidget(camera_combo)

        # Confirm button
        confirm_button = QPushButton("Load Camera", dialog)
        confirm_button.clicked.connect(lambda: self.load_selected_camera(camera_combo, dialog))
        layout.addWidget(confirm_button)

        dialog.exec()

    def load_selected_camera(self, camera_combo, dialog):
        """
        Loads the selected camera based on user input.
        """
        selected_camera_index = int(camera_combo.currentText().split()[-1])
        self.video_capture = cv2.VideoCapture(selected_camera_index, cv2.CAP_DSHOW)
        if not self.video_capture.isOpened():
            QMessageBox.critical(self, "Error", f"Could not open Camera {selected_camera_index}!")
        else:
            QMessageBox.information(self, "Camera Loaded", f"Camera {selected_camera_index} is now active.")
            self.playing = True
            self.timer.start(30)
            dialog.accept()
            
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
            
            height, width, _ = frame.shape
            self.frame_size = (width, height)
            
            if self.video_writer is not None:
                self.video_writer.write_frame(frame)
            
            for i, roi in enumerate(self.rois):
                x, y, w, h = roi.rect.x(), roi.rect.y(), roi.rect.width(), roi.rect.height()
                roi_frame = frame[y:y+h, x:x+w]

                # Perform analysis and update cross position
                avg_flow_x, avg_flow_y = roi.analysis_module.analyze(roi_frame)
                
                
                
                if avg_flow_x is not None and avg_flow_y is not None:
                    self.auto_save(roi, i)
                    roi.update_cross_position(avg_flow_x, avg_flow_y)

                roi.draw_on_frame(frame, i)
                roi.update_scrolling_axis(self.movement_buffers, self.movement_curves, self.max_frames, self.plot_widget)

            # Convert frame to RGB and display in QLabel
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            q_img = QImage(frame.data, width, height, channel * width, QImage.Format_RGB888)
            self.current_pixmap = QPixmap.fromImage(q_img)
            # self.video_canvas_label.setPixmap(self.current_pixmap)

            self.video_canvas_label.setPixmap(self.current_pixmap)
          
    def start_drawing_roi(self):
        if not self.arrow_locked:
            self.message_boxes("Confirm Direction")

        self.drawing_roi = True

    def mouse_press_event(self, event):
        if self.drawing_roi:
            # Adjust the start position based on scaling and offsets
            self.current_roi_start = self.adjust_mouse_position(event.pos())
            
        if self.drawing_arrow:
            self.arrow.start = self.adjust_mouse_position(event.pos())
        
    def mouse_move_event(self, event):
        if self.drawing_roi and self.current_roi_start:
            # Adjust the current position while dragging
            end = self.adjust_mouse_position(event.pos())
            start = self.current_roi_start
            self.current_roi_rect = QRect(start, end)
            self.update_video_with_roi()
        
        if self.drawing_arrow:
            self.arrow.end = self.adjust_mouse_position(event.pos())
            self.update_video_with_arrow()
            
    def mouse_release_event(self, event):
        
        if self.drawing_roi:
            # Adjust the end position
            end = self.adjust_mouse_position(event.pos())
            start = self.current_roi_start
            self.current_roi_rect = QRect(start, end)
            if (self.current_roi_rect.width() > 0 and 
                self.current_roi_rect.height() > 0 and 
                start.x() >= 0 and start.y() >= 0 and 
                end.x() >= 0 and end.y() >= 0):
                new_roi = ROI(self.current_roi_rect,
                              self.arrow.arrow_dir_x,
                              self.arrow.arrow_dir_y)  
                self.rois.append(new_roi)
                QMessageBox.information(self, "ROI Added", f"ROI #{len(self.rois)} added.")
            else:
                QMessageBox.warning(self, "Invalid ROI", "The drawn ROI is invalid.")
            self.drawing_roi = False
            self.current_roi_start = None
            self.current_roi_rect = None
            self.update()
            
        if self.drawing_arrow and self.arrow:
            self.arrow.end = self.adjust_mouse_position(event.pos())
            self.arrow.calculate_angle()
            self.update_video_with_arrow()
            self.drawing_arrow = False
            self.update_overflow_direction_textbox()
            print("Angel:", self.arrow.angle)
            print("Arrow Dir X:", self.arrow.arrow_dir_x)
            print("Arrow Dir Y:", self.arrow.arrow_dir_y)

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
        
        diff_height = pixmap_height - label_height
        diff_width = pixmap_width - label_width

        # Adjust for scaling
        adjusted_x = int(pos.x() + diff_width/2)
        adjusted_y = int(pos.y() + diff_height/2) 

        return QPoint(adjusted_x, adjusted_y)
    
    def update_overflow_direction_textbox(self):
        if self.arrow_locked:
            self.message_boxes("Arrow Locked")
            return
        
        if self.arrow:
            self.arrow_angle = self.arrow.angle
            self.direction_textbox.setText(f"{np.degrees(self.arrow_angle):.2f}")
            
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

    def update_video_with_arrow(self):
        """
        Overlay the arrow on the video canvas.
        """
        if self.current_pixmap and self.arrow and self.arrow.start and self.arrow.end:
            temp_pixmap = self.current_pixmap.copy()
            painter = QPainter(temp_pixmap)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            # Draw the arrow line
            painter.drawLine(self.arrow.start, self.arrow.end)
            # Draw arrowhead
            dx = self.arrow.end.x() - self.arrow.start.x()
            dy = self.arrow.end.y() - self.arrow.start.y()
            angle = np.arctan2(-dy, dx)
            length = 10  # Length of arrowhead lines
            x1 = self.arrow.end.x() - length * np.cos(angle - np.pi / 6)
            y1 = self.arrow.end.y() + length * np.sin(angle - np.pi / 6)
            x2 = self.arrow.end.x() - length * np.cos(angle + np.pi / 6)
            y2 = self.arrow.end.y() + length * np.sin(angle + np.pi / 6)
            painter.drawLine(self.arrow.end, QPoint(int(x1), int(y1)))
            painter.drawLine(self.arrow.end, QPoint(int(x2), int(y2)))
            painter.end()
            self.video_canvas_label.setPixmap(temp_pixmap)

    def manual_arrow_angle_update(self):
        """
        Update the arrow direction based on the value entered in the textbox.
        """
        try:
            # Parse the user input and update the arrow angle
            self.arrow_angle = np.radians(float(self.direction_textbox.text()))
            QMessageBox.information(self, "Direction Updated", f"Overflow direction set to {np.degrees(self.arrow_angle):.2f}°.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value for the overflow direction.")

    def asking_lock_arrow_direction(self):
        if self.arrow_locked:
            self.message_boxes("Arrow Locked")
            return
            
        self.message_boxes("Confirm Direction")
         
    def lock_arrow_direction(self):
        """
        Lock the arrow direction, preventing further modifications.
        """
        try:
            # Parse angle from the textbox
            self.arrow_angle = np.radians(float(self.direction_textbox.text()))
            self.arrow_locked = True
            self.arrow.angle = self.arrow_angle
            self.arrow.set_displaying_preset(self.video_canvas_label)
            self.arrow.update_arrow_canvas()
            self.auto_saver.update_arrow_direction(self.arrow_angle)
            QMessageBox.information(self, "Direction Locked", f"Overflow direction locked at {np.degrees(self.arrow_angle):.2f}°.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value for the overflow direction.")

    def start_recording(self):
        if not self.video_capture or not self.video_capture.isOpened():
            QMessageBox.warning(self, "Warning", "No active video feed to record.")
            return

        # Configure the video writer
        # file_name = QFileDialog.getSaveFileName(self, "Save Video", "", "Video Files (*.mp4 *.avi)")[0]
        # if not file_name:
        #     return  # User canceled
        
        if self.export.video_directory and self.export.record_video:
            
            file_path = self.export.video_directory
            file_name = self.export.video_filename
            
            self.video_writer = VideoRecorder(file_path, file_name, frame_size = self.frame_size)
            self.video_writer.start_recording()
            self.recording = True
            
            self.start_record_button.setText("Stop Recording")
            self.start_record_button.setStyleSheet("background-color: red; color: white;")
            self.start_record_button.clicked.disconnect(self.start_recording)
            self.start_record_button.clicked.connect(self.stop_recording)
        
        else:
            QMessageBox.warning(self, "Warning", "Recording is disabled.\nPlease enable it in the export settings.")
            return
        
    def stop_recording(self):
        if self.recording and self.video_writer:
            self.video_writer.stop_recording()
            # self.video_writer.release()
            self.video_writer = None
            self.recording = False

            self.start_record_button.setText("Start Recording")
            self.start_record_button.setStyleSheet("background-color: none;")
            self.start_record_button.clicked.disconnect(self.stop_recording)
            self.start_record_button.clicked.connect(self.start_recording)
            
            QMessageBox.information(self, "Recording Stopped", "Video recording has been saved")
    
    def auto_save(self, roi, roi_index):
        velocity = roi.analysis_module.velocity_history[-1]["velocity"]
        timestamp = roi.analysis_module.velocity_history[-1]["timestamp"]
        frame_index = roi.analysis_module.get_frame_count()
        
        self.auto_saver.add_frame_data(roi_index, frame_index, velocity, timestamp)
    
    def close_event(self, event):
        
        if self.video_writer:
            self.video_writer.release()
        super().closeEvent(event)
      
    def save(self):
        try:
            # Step 1: Save analysis results
            if not self.export.export_directory or not self.export.export_filename:
                QMessageBox.warning(self, "Export Error", "Please configure export settings before saving.")
                return

            self.export_data()

            # Step 3: Stop video playback
            self.timer.stop()
            if self.video_capture:
                self.video_capture.release()

            # Notify user of success
            QMessageBox.information(
                self,
                "Save Successful",
                f"All data and settings have been saved:\n"
                f"- Results exported to: {self.export.export_directory}\n",
            )

            # Step 4: Reset the application state
            self.reset_application()

        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"An error occurred while saving data: {e}")

    def export_data(self):
        """
        Handles exporting data for the program.
        """
        self.export.excel_resutls(self.rois, self.arrow_angle)

    def reset_application(self):
        """
        Resets the application state.
        """
        self.rois = []
        self.movement_buffers = {}
        self.movement_curves = {}
        self.plot_widget.clear()
        self.video_canvas_label.clear()
        
        self.arrow.reset()
        self.arrow_locked = False
        self.arrow_canvas_label.clear()
        
        self.export.export_filename = datetime.now().strftime("%Y%m%d")
        
        # Reinitialize UI components if necessary
        QMessageBox.information(self, "Reset Complete", "The application has been reset. You can now start a new mission.")
             
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())

