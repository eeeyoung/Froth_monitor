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
from .image_analysis import VideoAnalysisModule

class ROI:
    def __init__(self, 
                 rect: QRect, 
                 arrow_dir_x: float, 
                 arrow_dir_y: float):
        self.rect = rect
        self.analysis_module = VideoAnalysisModule(arrow_dir_x,
                                                   arrow_dir_y)
        self.cross_position = QPoint(rect.center().x(), rect.center().y())  # Initialize cross at ROI center

    def update_cross_position(self, avg_flow_x, avg_flow_y):
        """
        Update the cross intersection position based on the optical flow results.
        The position wraps around when it goes out of the ROI.
        """      
        
        # Update cross position within the ROI bounds
        new_x = self.cross_position.x() + int(avg_flow_x)
        new_y = self.cross_position.y() + int(avg_flow_y)

        # Wrap around horizontally
        if new_x < self.rect.left():
            new_x = self.rect.right() - (self.rect.left() - new_x)
        elif new_x > self.rect.right():
            new_x = self.rect.left() + (new_x - self.rect.right())

        # Wrap around vertically
        if new_y < self.rect.top():
            new_y = self.rect.bottom() - (self.rect.top() - new_y)
        elif new_y > self.rect.bottom():
            new_y = self.rect.top() + (new_y - self.rect.bottom())

        self.cross_position.setX(new_x)
        self.cross_position.setY(new_y)

    def draw_on_frame(self, frame, roi_index):
        """
        Draws the ROI rectangle, cross position, and scrolling axis on the given frame.
        """
        x, y, w, h = self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()

        # Draw ROI rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Draw X-axis and Y-axis through the ROI
        cross_x = self.cross_position.x()
        cross_y = self.cross_position.y()

        # X-axis: Horizontal line across the ROI
        cv2.line(frame, (x, cross_y), (x + w, cross_y), self.analysis_module.color, 2)

        # Y-axis: Vertical line across the ROI
        cv2.line(frame, (cross_x, y), (cross_x, y + h), self.analysis_module.color, 2)

        # Draw ROI label at the top-right corner
        label = f"ROI {roi_index + 1}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + w - text_size[0] - 5  # Right-align the text
        text_y = y + text_size[1] + 5  # Slightly below the top-right corner
        cv2.putText(
            frame,
            label,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,  # Font scale
            (0, 255, 0),  # Color (green)
            1,  # Thickness
            cv2.LINE_AA,
        )
    
    def update_scrolling_axis(self, movement_buffers, movement_curves, max_frames, plot_widget):
        """
        Updates the scrolling axis data and renders it on the plot widget.
        """
        if self not in movement_buffers:
            movement_buffers[self] = [0] * max_frames

        # Update movement buffer
        if len(movement_buffers[self]) >= max_frames:
            movement_buffers[self].pop(0)

        movement_buffers[self].append(self.analysis_module.current_velocity)

        # Update or create the curve
        if self not in movement_curves:
            curve_color = pg.mkColor(self.analysis_module.color)  # Use the ROI's assigned color
            movement_curves[self] = plot_widget.plot(
                pen=pg.mkPen(color=curve_color, width=2)
            )

        movement_curves[self].setData(movement_buffers[self])
        
class Arrow:
    def __init__(self, 
                 canvas_label: QLabel,
                 start: QPoint = None, 
                 end: QPoint = None):
        """
        Initialize the Arrow object with a starting and ending point.
        The angle of the arrow will be calculated from the starting and ending points.
        If the starting and ending points are not provided, they will be set to None.
        """
        self.canvas_label = canvas_label
        self.start = start  # Starting point of the arrow
        self.end = end      # Ending point of the arrow
        self.angle = 0.0    # Angle of the arrow (in radians)
        self.arrow_dir_x = 0.0
        self.arrow_dir_y = 0.0
        
    def calculate_angle(self):
        """
        Calculate the angle of the arrow in radians relative to the horizontal.
        """
        if self.start and self.end:
            dx = self.end.x() - self.start.x()
            dy = self.end.y() - self.start.y()
            self.angle = np.arctan2(dy, dx)

    def calculate_components_angles(self):
        self.arrow_dir_x = np.cos(self.angle)
        self.arrow_dir_y = np.sin(self.angle)
    
    def update_arrow_canvas(self):
        
        # Prepare the painter
        pixmap = self.canvas_label.pixmap() or QPixmap(self.canvas_label.size())
        pixmap.fill(Qt.transparent)  # Clear previous drawing
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Arrow attributes
        canvas_width = self.canvas_label.width()
        canvas_height = self.canvas_label.height()
        center = QPoint(canvas_width // 2, canvas_height // 2)
        arrow_length = min(canvas_width, canvas_height) // 3

        # Calculate arrow start and end points
        start_x = center.x() - arrow_length * self.arrow_dir_x
        start_y = center.y() - arrow_length * self.arrow_dir_y
        end_x = center.x() + arrow_length * self.arrow_dir_x
        end_y = center.y() + arrow_length * self.arrow_dir_y

        # Draw arrow line
        painter.drawLine(QPoint(int(start_x), int(start_y)), QPoint(int(end_x), int(end_y)))

        # Draw arrowhead
        arrow_head_length = 10
        left_x = end_x - arrow_head_length * np.cos(self.angle - np.pi / 6)
        left_y = end_y - arrow_head_length * np.sin(self.angle - np.pi / 6)
        right_x = end_x - arrow_head_length * np.cos(self.angle + np.pi / 6)
        right_y = end_y - arrow_head_length * np.sin(self.angle + np.pi / 6)

        painter.drawLine(QPoint(int(end_x), int(end_y)), QPoint(int(left_x), int(left_y)))
        painter.drawLine(QPoint(int(end_x), int(end_y)), QPoint(int(right_x), int(right_y)))

        painter.end()

        # Set updated pixmap
        self.canvas_label.setPixmap(pixmap)

    def set_displaying_preset(self, video_canvas_label):
            """
            Sets up the arrow's start and end points based on the current angle for the video canvas.
            :param video_canvas_label: The QLabel representing the video canvas.
            """
            self.calculate_components_angles()

            # Define the arrow start and end points
            canvas_width = video_canvas_label.width()
            canvas_height = video_canvas_label.height()

            # Arrow starts at the canvas center
            start_x = canvas_width - 100
            start_y = canvas_height - 100

            # Arrow extends in the direction of the angle
            arrow_length = 60  # Set a fixed length for the arrow
            end_x = int(start_x + arrow_length * self.arrow_dir_x)
            end_y = int(start_y + arrow_length * self.arrow_dir_y)

            self.arrow_start = QPoint(start_x, start_y)
            self.arrow_end = QPoint(end_x, end_y)
    
    def reset(self):
        self.angle = 0.0    # Angle of the arrow (in radians)
        self.arrow_dir_x = 0.0
        self.arrow_dir_y = 0.0
        
class Export:
    def __init__(self, parent=None):
        self.parent = parent
        self.export_directory = ""
        self.export_filename = datetime.now().strftime("%Y%m%d")

    def export_setting_window(self):
        """
        Opens a dialog for configuring export settings.
        """
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Export Settings")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Export Directory Selection
        directory_label = QLabel("Export Directory:", dialog)
        layout.addWidget(directory_label)

        directory_button = QPushButton("Select Directory", dialog)
        directory_button.clicked.connect(lambda: self.select_export_directory(dialog))
        layout.addWidget(directory_button)

        # Add QLabel to display the selected directory and set an object name
        directory_display = QLabel(self.export_directory if self.export_directory else "Not selected", dialog)
        directory_display.setObjectName("directory_display")  # Assign a unique name for findChild
        layout.addWidget(directory_display)

        # Export Filename Input
        filename_label = QLabel("Export Filename (without extension):", dialog)
        layout.addWidget(filename_label)

        filename_input = QLineEdit(self.export_filename, dialog)
        layout.addWidget(filename_input)

        # Save Button
        save_button = QPushButton("Save Settings", dialog)
        save_button.clicked.connect(lambda: self.save_export_settings(dialog, filename_input))
        layout.addWidget(save_button)

        dialog.exec()

    def select_export_directory(self, parent_dialog):
        """
        Opens a file dialog to select the export directory.
        """
        directory = QFileDialog.getExistingDirectory(self.parent, "Select Export Directory")
        if directory:
            self.export_directory = directory

            # Update directory label in the parent dialog
            directory_display = parent_dialog.findChild(QLabel, "directory_display")
            if directory_display:  # Ensure the QLabel is found
                directory_display.setText(self.export_directory)

    def save_export_settings(self, dialog, filename_input):
        """
        Saves the export settings.
        """
        # Save the entered filename
        self.export_filename = filename_input.text()

        # Display a warning if the directory is not set
        if not self.export_directory:
            QMessageBox.warning(self.parent, "Warning", "Export directory is not set.")
            return

        QMessageBox.information(
            self.parent,
            "Settings Saved",
            f"Export settings saved:\nDirectory: {self.export_directory}\nFilename: {self.export_filename}"
        )
        dialog.accept()
        
    def excel_resutls(self, rois, arrow_angle):
        """
        Handles exporting data for the program.
        """
        try:
            # Check if export directory and filename are set
            if not self.export_directory or not self.export_filename:
                QMessageBox.warning(self.parent,
                                    "Export Error",
                                    "Please configure export settings before exporting.")
                return
            
            # Prepare the full file path
            file_path_csv = f"{self.export_directory}/{self.export_filename}.csv"
            # file_path_json = f"{self.export_directory}/{self.export_filename}.json"

            # Step 1: Collect data
            export_data = self.collect_export_data(rois, arrow_angle)

            # Step 2: Write to both CSV and JSON
            self.write_csv(file_path_csv, export_data)

            QMessageBox.information(
                self.parent,
                "Export Successful",
                f"Data successfully exported:\n- CSV: {file_path_csv}\n-",
            )

        except Exception as e:
            QMessageBox.critical(self.parent,
                                 "Export Failed",
                                 f"An error occurred during export: {e}")

    def collect_export_data(self, rois, arrow_angle):
        
        data = {
            "arrow_direction": np.degrees(arrow_angle),  # Convert to degrees
            "roi_data": [],
        }
        
        for i, roi in enumerate(rois):
            roi_data = {
                "ROI Index": i + 1,
                "Movement Data": [],
            }
            
            
            for frame_index, delta in enumerate(roi.analysis_module.get_results()):
                print("frame_index", frame_index + 1)
                print("delta", delta)
                roi_data["Movement Data"].append({
                    "Frame Index": frame_index + 1,
                    "Velocity": delta
                })
                
            data["roi_data"].append(roi_data)
            
        print(data)
        return data
    
    def write_csv(self, file_path, data):
        """
        Writes the export data to an Excel file, with each ROI in a separate sheet.
        """
        wb = Workbook()

        # Add the arrow direction in the first sheet
        arrow_sheet = wb.active
        arrow_sheet.title = "Arrow Direction"
        arrow_sheet.append(["Arrow Direction (degrees)"])
        arrow_sheet.append([data["arrow_direction"]])

        # Create separate sheets for each ROI
        for roi in data["roi_data"]:
            sheet_name = f"ROI {roi['ROI Index']}"
            ws = wb.create_sheet(title=sheet_name)

            # Add headers
            ws.append(["Frame Index", "Velocity(pixels/frame)"])

            # Add movement data
            for movement in roi["Movement Data"]:
                ws.append([movement["Frame Index"], movement["Velocity"]])

        # Save the workbook
        wb.save(file_path)

class AutoSaver:
    def __init__(self, 
                 file_path = "data/auto_save",
                 file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")):
        
        self.file_path = f"{file_path}/{file_name}.json"
        self.data = {
            "arrow_direction": None,
            "roi_data": []
        }
    
    def update_arrow_direction(self, arrow_angle):
        self.data["arrow_direction"] = float(arrow_angle)  # Store as float
    
    def add_frame_data(self, roi_index, frame_index, velocity):
        # Ensure the ROI exists
        while len(self.data["roi_data"]) <= roi_index:
            self.data["roi_data"].append({"ROI Index": len(self.data["roi_data"]) + 1, "Movement Data": []})

        velocity = float(velocity)
        roi_index = int(roi_index)
        frame_index = int(frame_index)
        
        # Append movement data
        self.data["roi_data"][roi_index]["Movement Data"].append({
            "Frame Index": frame_index,
            "Velocity": velocity
        })
        self.save_to_file()  # Save every update
    
    def save_to_file(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.data, f, indent=4)
        except TypeError as e:
            print(f"Serialization error: {e}")
            print(f"Problematic data: {self.data}")
            raise
    
    def load_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
                return self.data
        return None        

class VideoRecorder:
    def __init__(self, file_name="./recording", fps=30, frame_size=(640, 480)):
        """
        Initialize the VideoRecorder.
        
        Args:
            output_directory (str): Directory to save the video file.
            filename_prefix (str): Prefix for the video file name.
            fps (int): Frames per second for the recording.
            frame_size (tuple): Width and height of the video frames.
        """
        # self.output_directory = output_directory
        # self.filename_prefix = filename_prefix
        self.file_name = file_name
        self.fps = fps
        self.frame_size = frame_size
        self.recording = False
        self.writer = None
        self.filepath = None

    def start_recording(self):
        """
        Start recording video to a file.
        """
        # if not os.path.exists(self.output_directory):
        #     os.makedirs(self.output_directory)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = f"{self.file_name}.mp4"

        self.writer = cv2.VideoWriter(
            self.filepath,
            cv2.VideoWriter_fourcc(*'XVID'),
            self.fps,
            self.frame_size
        )
        
        self.recording = True
        print(f"Recording started. Saving to {self.filepath}")

    def write_frame(self, frame):
        """
        Write a single frame to the video file.
        
        Args:
            frame: The video frame to write.
        """
        if self.recording and self.writer.isOpened():
            self.writer.write(frame)
            print("Frame written to video file")
        else:
            print("Writer is not opened or recording is stopped")

    def stop_recording(self):
        """
        Stop recording and release resources.
        """
        if self.writer:
            self.writer.release()
            self.writer = None
        self.recording = False
        print(f"Recording stopped. Video saved at {self.filepath}")

    def is_recording(self):
        """
        Check if the recorder is currently recording.
        
        Returns:
            bool: True if recording, False otherwise.
        """
        return self.recording
        
        
        
        
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
        grid_layout.addWidget(self.direction_textbox, 3, 1, 1, 1)
        
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
        layout.addWidget(self.add_roi_button, 1, 0, 1, 2)

        self.pause_play_button = QPushButton("Pause/Play", self)
        self.pause_play_button.clicked.connect(self.pause_play)
        layout.addWidget(self.pause_play_button, 2, 0, 1, 2)

        self.confirm_arrow_button = QPushButton("Confirm Arrow Direction", self)
        self.confirm_arrow_button.clicked.connect(self.asking_lock_arrow_direction)
        layout.addWidget(self.confirm_arrow_button, 4, 0, 1, 2)
        
        self.save_end_button = QPushButton("Save and End Playing", self)
        self.save_end_button.clicked.connect(self.save_end)
        layout.addWidget(self.save_end_button, 5, 0, 1, 2)
        
        self.start_record_button = QPushButton("Start Recording", self)
        self.start_record_button.clicked.connect(self.start_recording)
        self.start_record_button.setStyleSheet("background-color: green; color: white;")
        layout.addWidget(self.start_record_button, 7, 0, 1, 2)

        self.stop_record_button = QPushButton("Stop Recording", self)
        self.stop_record_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_record_button, 8, 0, 1, 2)

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
        
        self.add_arrow_button = QPushButton("Add Overflow Direction")
        self.add_arrow_button.clicked.connect(self.start_drawing_arrow)
        layout.addWidget(self.add_arrow_button, 3, 0, 1, 1)

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
        file_name = QFileDialog.getSaveFileName(self, "Save Video", "", "Video Files (*.mp4 *.avi)")[0]
        if not file_name:
            return  # User canceled
        
        print(self.video_canvas_label.width())
        print(int(self.video_canvas_label.height()))
        self.video_writer = VideoRecorder(file_name, frame_size = self.frame_size)
        self.video_writer.start_recording()
        self.recording = True
        
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for .mp4 files
        # fps = int(self.video_capture.get(cv2.CAP_PROP_FPS)) or 30  # Fallback to 30 FPS
        # frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        # frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # self.video_writer = cv2.VideoWriter(file_name, fourcc, fps, (frame_width, frame_height))
        # self.recording = True
        
        QMessageBox.information(self, "Recording Started", f"Recording to {file_name}")
    
    def stop_recording(self):
        if self.recording and self.video_writer:
            self.video_writer.stop_recording()
            # self.video_writer.release()
            self.video_writer = None
            self.recording = False
            QMessageBox.information(self, "Recording Stopped", "Video recording has been saved.")
    
    def auto_save(self, roi, roi_index):
        velocity = roi.analysis_module.velocity_history[-1]
        frame_index = roi.analysis_module.get_frame_count()
        self.auto_saver.add_frame_data(roi_index, frame_index, velocity)
    
    def close_event(self, event):
        
        if self.video_writer:
            self.video_writer.release()
        super().closeEvent(event)
      
    def save_end(self):
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
        
        self.export.export_directory = ""
        self.export.export_filename = datetime.now().strftime("%Y%m%d")
        
        # Reinitialize UI components if necessary
        QMessageBox.information(self, "Reset Complete", "The application has been reset. You can now start a new mission.")
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())


# Save all the data from beginning - json, in case of crashing or sth else
# Before running, finish setup of export setting, roi drawing, overflow_direction, and arrow direction


# Save the real-time video (as option for user) ?

# Combination of software & variographic analysis?