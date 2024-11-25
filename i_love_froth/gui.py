<<<<<<< HEAD
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
                                QMenuBar, QMenu, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                                QComboBox, QMessageBox, QDialog, QLineEdit)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QImage
=======
"""Froth Tracker Application.

This Python-based GUI application is designed to analyze froth images and videos for research and industrial purposes. 
The program uses OpenCV for image processing and PySide6 for GUI development. It incorporates real-time video input 
from cameras or local video files, enabling users to define regions of interest (ROIs) and track froth dynamics with 
optical flow analysis.

Key Features:
--------------
1. **Video and Camera Input**:
   - Supports importing local video files or using real-time camera input.
   - Dynamically calculates frames per second (FPS) for accurate frame analysis and recording.

2. **Region of Interest (ROI)**:
   - Allows users to draw rectangular ROIs directly on the video canvas.
   - Each ROI is individually tracked, with velocities and other metrics computed using Farneback Optical Flow.

3. **Overflow Direction Arrow**:
   - Users can draw an arrow indicating the overflow direction, which is used in ROI analysis.
   - The arrow direction can be manually adjusted or locked for analysis.

4. **Real-time Video Recording**:
   - Records input video with synchronized timestamps.
   - Saves recorded video in real-time to prevent data loss in case of a crash.

5. **Data Export**:
   - Saves analysis results, including velocities and timestamps, to JSON, CSV, and Excel formats.
   - Includes features to calculate per-second velocities and exports them with the analysis data.

6. **Auto-Save and Crash Resilience**:
   - Periodically saves analysis data, ensuring minimal data loss.
   - Users can reload video and continue analysis after a crash.

7. **Customizable Export Settings**:
   - Allows configuration of export directories, filenames, and video saving preferences.
   - Provides options for saving recorded videos in the same directory or a custom directory.

8. **Flexible UI Design**:
   - Interactive GUI with responsive layouts for video canvas, arrow canvas, and ROI movement graphs.
   - Easy-to-use buttons for starting/stopping analysis, resetting the application, and managing export settings.

Structure:
-----------
1. **MainGUI**:
   - Core class that manages the application’s main window and handles video playback, ROI management, and event handling.

2. **Arrow**:
   - Handles drawing and updating the overflow direction arrow.

3. **ROI**:
   - Represents individual regions of interest, tracks their movement, and performs analysis.

4. **Export**:
   - Handles exporting analysis results to different file formats.

5. **VideoRecorder**:
   - Manages real-time video recording and ensures video files are saved during recording.

6. **AutoSaver**:
   - Periodically saves analysis data to prevent loss in case of crashes.

Requirements:
--------------
- Python 3.10 or higher
- PySide6
- OpenCV
- pyqtgraph
- openpyxl
- NumPy

Usage:
------
1. Install dependencies using the requirements.txt file: pip install -r requirements.txt
2. Run the application
3. Import a video file or load a camera input.
4. Draw ROIs and an overflow direction arrow for analysis.
5. Start video recording and export the analysis results.

"""

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
                                QMenuBar, QMenu, QWidget, QVBoxLayout, QGridLayout, 
                                QComboBox, QMessageBox, QDialog, QLineEdit)
from PySide6.QtGui import QPixmap, QPainter, QPen, QImage, QCloseEvent, QMouseEvent
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
import pyqtgraph as pg
import sys
import cv2
<<<<<<< HEAD
import csv
import json
import os
import numpy as np
from datetime import datetime
from openpyxl import Workbook
=======
import time
import numpy as np
from datetime import datetime
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
from .arrow import Arrow
from .autosaver import AutoSaver
from .video_recorder import VideoRecorder
from .roi import ROI
from .export import Export
        
class MainGUI(QMainWindow):
<<<<<<< HEAD
    def __init__(self):
        """
        Initializes the main GUI window with essential attributes and UI elements.

        :param self: The main GUI window instance
        :type self: MainGUI
        :return: None
        :rtype: None
=======
    """
    The main graphical user interface (GUI) class for the Froth Tracker application.

    This class provides the primary interface for the application, allowing users to:
    - Load video inputs (local files or live camera feed).
    - Define and analyze regions of interest (ROIs).
    - Visualize optical flow data in real-time.
    - Configure export settings and save analysis results.
    - Record and save live video streams.

    Attributes:
    ----------
    video_capture : cv2.VideoCapture
        Object to capture video from a file or camera feed.
    timer : QTimer
        Timer object for controlling frame updates in real-time.
    playing : bool
        Indicates whether the video or camera feed is currently playing.
    rois : list[ROI]
        List of Region of Interest (ROI) objects for tracking and analysis.
    current_roi_start : QPoint or None
        Starting point for the currently drawn ROI.
    current_roi_rect : QRect or None
        Rectangle representing the currently drawn ROI.
    drawing_roi : bool
        Flag indicating whether an ROI is currently being drawn.
    current_pixmap : QPixmap or None
        Pixmap representing the current video frame for real-time updates.
    arrow_angle : float
        Angle of the overflow direction arrow in radians (default: π/2 or 90°).
    arrow_locked : bool
        Indicates whether the arrow direction is locked.
    drawing_arrow : bool
        Flag to indicate if an arrow is being drawn.
    overflow_direction_label : QLabel
        Label displaying the overflow direction angle.
    export : Export
        Instance of the Export class for managing export-related functionality.
    recording : bool
        Indicates whether video recording is active.
    video_writer : VideoRecorder or None
        Instance of the VideoRecorder class for managing video recording.
    fps_recording : int
        Frames per second of the video recording.
    realtime_input : bool
        Indicates whether the input is a real-time camera feed.
    auto_saver : AutoSaver
        Instance of the AutoSaver class for periodically saving data.

    Methods:
    -------
    __init__():
        Constructor to initialize the main GUI and its components.
    initUI():
        Initializes the main window layout and UI elements.
    createMenuBar():
        Creates the menu bar with import and export options.
    add_buttons(layout: QGridLayout):
        Adds control buttons (e.g., Play/Pause, Add ROI, Save) to the UI layout.
    add_canvas_placeholder(layout: QGridLayout):
        Adds a placeholder for the video canvas.
    add_arrow_canvas(layout: QGridLayout):
        Adds a placeholder for the arrow direction canvas.
    add_ROI_movement_placeholder(layout: QGridLayout):
        Adds a plot widget for visualizing ROI movement data.
    add_overflow_direction_label(layout: QGridLayout):
        Adds a button for adding the overflow direction arrow.
    message_boxes(event: str):
        Displays message boxes for confirmation and warnings.
    start_drawing_arrow():
        Initiates drawing of the overflow direction arrow.
    import_local_video():
        Opens a dialog to load a local video file.
    load_camera_dialog():
        Opens a dialog to select and load a live camera feed.
    load_selected_camera(camera_combo: QComboBox, dialog: QDialog):
        Loads the selected camera based on user input.
    pause_play():
        Toggles video playback state.
    display_frame():
        Reads and processes frames from the video capture for real-time display.
    start_drawing_roi():
        Starts drawing a new ROI on the video canvas.
    mouse_press_event(event: QMouseEvent):
        Handles mouse press events for ROI and arrow drawing.
    mouse_move_event(event: QMouseEvent):
        Handles mouse move events for ROI and arrow drawing.
    mouse_release_event(event: QMouseEvent):
        Handles mouse release events for ROI and arrow drawing.
    adjust_mouse_position(pos: QPoint) -> QPoint:
        Adjusts the mouse position relative to the displayed video frame.
    update_overflow_direction_textbox():
        Updates the overflow direction angle in the textbox.
    update_video_with_roi():
        Overlays the currently drawn ROI on the video frame.
    update_video_with_arrow():
        Overlays the currently drawn arrow on the video frame.
    manual_arrow_angle_update():
        Updates the arrow direction based on user input in the textbox.
    asking_lock_arrow_direction():
        Prompts the user to lock the arrow direction.
    lock_arrow_direction():
        Locks the overflow direction arrow and saves the angle.
    fps_calculation():
        Calculates the frames per second (FPS) of the video input.
    start_recording():
        Initiates video recording to a specified directory.
    stop_recording():
        Stops video recording and saves the recorded video.
    auto_save(roi: ROI, roi_index: int):
        Periodically saves ROI data and velocities.
    close_event(event: QCloseEvent):
        Handles actions when the main window is closed.
    save():
        Saves the current application state and analysis results.
    export_data():
        Exports analysis results to the configured directory.
    reset_application():
        Resets the application to its initial state for a new session.

    """
    
    def __init__(self) -> None:
        """
        Constructor for the MainGUI class.
        
        Initializes the main window and the video/ROI-related attributes.
        Also initializes the arrow drawing, export setting, video recording, and auto save attributes.
        Finally, defines the UI elements by calling the initUI method.
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        super(MainGUI, self).__init__()
        self.setWindowTitle('I love Froths')
        self.setGeometry(100, 100, 1200, 600)
        
        # Video-related attributes
<<<<<<< HEAD
        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.playing = False
        
        # ROI and Video Analysis
        self.rois = []  # List of ROI instances
=======
        self.video_capture: cv2.VideoCapture = None
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.playing: bool = False
        
        # ROI and Video Analysis
        self.rois: list = []  # List of ROI instances
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.current_roi_start = None  # Starting point of the currently drawn ROI
        self.current_roi_rect = None  # QRect of the ROI being drawn
        self.drawing_roi = False  # Flag for ROI drawing
        self.current_pixmap = None  # Store the current video frame as QPixmap for real-time updates
        
        # Arrow drawing
<<<<<<< HEAD
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
=======
        self.arrow_angle: float = np.pi / 2
        self.arrow_locked: bool = False # Lock status for arrow direction
        self.drawing_arrow: bool = False  # Flag to indicate if arrow is being drawn
        self.overflow_direction_label: QLabel = None  # Label to display the overflow direction angle
        
        # Export setting
        self.export: Export = Export(self)
        
        # Video recording
        self.recording: bool = False
        self.video_writer: VideoRecorder = None
        self.fps_recording: int = 0
        self.realtime_input: bool = False
        
        # Auto Save
        self.auto_saver: AutoSaver = AutoSaver()
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.auto_saver.load_from_file
        
        
        # Define UI elements
        self.initUI()

<<<<<<< HEAD
    def initUI(self):
=======
    def initUI(self) -> None:
        """
        Initialize the UI elements of the main window.
        
        This function initializes the main window's layout, adds a menu bar, 
        a grid layout for buttons and the video canvas, and adds placeholders 
        for the video canvas, arrow canvas, ROI movements canvas, and the 
        overflow direction label and text box.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
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

<<<<<<< HEAD
        # Buttons
        # self.add_buttons(grid_layout)

        # Video canvas placeholder
        self.add_canvas_placeholder(grid_layout)

=======
        # Video canvas placeholder
        self.add_canvas_placeholder(grid_layout)

        # Arrow canvas
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.add_arrow_canvas(grid_layout)
        
        # Overflow direction label
        self.add_overflow_direction_label(grid_layout)

        # ROI Movements Canvas
        self.add_ROI_movement_placeholder(grid_layout)
        
<<<<<<< HEAD

        
=======
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        # Overflow direction value label
        self.direction_textbox = QLineEdit(self)
        self.direction_textbox.setText(f"{np.degrees(self.arrow_angle):.2f}")  # Default to 90 degrees
        self.direction_textbox.editingFinished.connect(self.manual_arrow_angle_update)
        self.direction_textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(self.direction_textbox, 1, 1, 1, 1)
        
        self.add_buttons(grid_layout)

<<<<<<< HEAD
    def createMenuBar(self):
=======
    def createMenuBar(self) -> None:
        """
        Create the menu bar for the main window.
        
        This function creates a menu bar with two menus: "Import" and "Export".
        The "Import" menu contains two actions: "Import Local Video" and "Load Camera".
        The "Export" menu contains one action: "Export Settings".
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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

<<<<<<< HEAD
    def add_buttons(self, layout):
=======
    def add_buttons(self, layout: QGridLayout) -> None:
        """
        Adds buttons to the layout for adding a ROI, pausing/resuming the video,
        confirming the arrow direction, saving the current state, resetting the application,
        and starting video recording.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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

<<<<<<< HEAD
        # self.stop_record_button = QPushButton("Stop Recording", self)
        # self.stop_record_button.clicked.connect(self.stop_recording)
        # layout.addWidget(self.stop_record_button, 9, 0, 1, 2)

    def add_canvas_placeholder(self, layout):
        
=======
    def add_canvas_placeholder(self, layout: QGridLayout) -> None:
        """
        Adds a placeholder QLabel to the layout where the video canvas will be drawn.
        The size of the label is fixed to 700x400.
        Also sets up mouse events for ROI drawing.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.video_canvas_label = QLabel("Video Canvas", self)
        self.video_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_canvas_label.setStyleSheet("background-color: none;")
        self.video_canvas_label.setFixedSize(700, 400)
        layout.addWidget(self.video_canvas_label, 0, 2, 8, 6)

        # Mouse events for ROI drawing
        self.video_canvas_label.mousePressEvent = self.mouse_press_event
        self.video_canvas_label.mouseMoveEvent = self.mouse_move_event
        self.video_canvas_label.mouseReleaseEvent = self.mouse_release_event
    
<<<<<<< HEAD
    def add_arrow_canvas(self, layout):
=======
    def add_arrow_canvas(self, layout: QGridLayout) -> None:
        """
        Adds a placeholder QLabel to the layout where the arrow direction
        will be drawn. The size of the label is fixed to 150x150.
        Also creates an instance of the Arrow class which will handle
        drawing the arrow.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.arrow_canvas_label = QLabel("Arrow Display", self)
        self.arrow_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrow_canvas_label.setStyleSheet("background-color: lightgray;")
        self.arrow_canvas_label.setFixedSize(150, 150)
        layout.addWidget(self.arrow_canvas_label, 7, 4, 1, 1)
        
        self.arrow = Arrow(self.arrow_canvas_label)  # Current arrow instance
    
<<<<<<< HEAD
    def add_ROI_movement_placeholder(self, layout):
=======
    def add_ROI_movement_placeholder(self, layout: QGridLayout) -> None:
        """
        Adds a placeholder for the ROI movement curves to the layout.
        
        Creates a PlotWidget instance and adds it to the layout. The widget is
        set to have a fixed size of 700x200 and the Y-axis scale is hidden.
        The X-axis scale is also hidden, and a legend is added to the plot.
        Also initializes the data structures to hold the movement curves and
        buffers for each ROI.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
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
        
<<<<<<< HEAD
    def add_overflow_direction_label(self, layout):
        
=======
    def add_overflow_direction_label(self, layout) -> None:
        """
        Adds a QPushButton to the layout which triggers the start_drawing_arrow method when clicked.
        The button is labeled "Add Overflow Arrow".
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.add_arrow_button = QPushButton("Add Overflow Arrow")
        self.add_arrow_button.clicked.connect(self.start_drawing_arrow)
        layout.addWidget(self.add_arrow_button, 1, 0, 1, 1)

<<<<<<< HEAD
    def message_boxes(self, event):
        if event == "Confirm Direction":

=======
    def message_boxes(self, event: str) -> None:
        """
        Handles different message box events related to the arrow direction.

        This function shows a message box for confirming the overflow direction
        and for warning the user if the overflow direction is already locked.
        
        Parameters:
        event (str): The type of event that triggered the message box.
        """
        
        if event == "Confirm Direction":
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            reply = QMessageBox.question(
                    self,
                    "Confirm Overflow Direction",
                    f"The current overflow direction is {float(self.direction_textbox.text()):.2f}°.\n"
                    "Would you like to lock this direction?",
                    QMessageBox.Yes | QMessageBox.No,
                )
<<<<<<< HEAD
            if reply == QMessageBox.Yes:
                self.lock_arrow_direction()
=======
            
            if reply == QMessageBox.Yes:
                self.lock_arrow_direction()
                
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            else:
                QMessageBox.warning(self, "Direction Not Confirmed", "Please confirm the arrow direction first.")
                return    
            
        if event == "Arrow Locked":
            QMessageBox.warning(self, "Warning", "Overflow Direction already locked")
            return    
        
<<<<<<< HEAD
    def start_drawing_arrow(self):
        if self.arrow_locked:

=======
    def start_drawing_arrow(self) -> None:
        """
        Initiate the drawing of an overflow direction arrow.

        This function sets the GUI state to allow the user to draw an arrow
        indicating the overflow direction. If the arrow direction is already 
        locked, the function returns immediately without any changes.
        """
            
        if self.arrow_locked:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            return
        
        self.drawing_arrow = True
        self.direction_textbox.setText("Drawing Overflow Direction...")
        return
    
<<<<<<< HEAD
    def import_local_video(self):
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
=======
    def import_local_video(self) -> None:
        """
        Opens a file dialog to select a local video file and initializes video capture.

        This function presents a file dialog to the user for selecting a video file
        with extensions .mp4, .avi, or .mkv. Upon selection, it attempts to open the
        video file using OpenCV's VideoCapture. If successful, it starts the video 
        playback by setting the playing flag to True and begins a timer with a 30 ms 
        interval. If the video cannot be opened, it shows a critical error message.
        """
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if file_path:
            self.video_capture = cv2.VideoCapture(file_path)
            if not self.video_capture.isOpened():
                QMessageBox.critical(self, "Error", "Could not open the video file!")
            else:
                self.playing = True
                self.timer.start(30)

<<<<<<< HEAD
    def load_camera_dialog(self):
        """
        Opens a dialog to select and load an available camera.
        """
=======
    def load_camera_dialog(self) -> None:
        """
        Opens a dialog to select and load an available camera.

        This function checks for available cameras by attempting to open up to 
        10 camera indices using OpenCV. If no cameras are detected, it displays 
        a critical error message. Otherwise, it presents a dialog with a dropdown 
        for selecting from the available cameras and a confirm button to load 
        the selected camera.

        If a camera is selected, the `load_selected_camera` method is called with 
        the selected camera index.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
<<<<<<< HEAD

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
=======
        
        # Show the dialog
        dialog.exec()

    def load_selected_camera(self, 
                             camera_combo: QComboBox, 
                             dialog: QDialog) -> None:
        
        """
        Loads the selected camera based on user input.

        This function is called when the user selects a camera from the
        dropdown in the camera selection dialog and clicks the "Load Camera"
        button. It attempts to open the selected camera with OpenCV and
        displays a critical error message if the camera could not be opened.
        If the camera is opened successfully, it displays an information
        message indicating which camera is now active and starts the timer
        for reading frames from the camera at a rate of 30 frames per second.
        """
        
        selected_camera_index = int(camera_combo.currentText().split()[-1])
        self.video_capture = cv2.VideoCapture(selected_camera_index, cv2.CAP_DSHOW)
        
        if not self.video_capture.isOpened():
            QMessageBox.critical(self, "Error", f"Could not open Camera {selected_camera_index}!")
            
        else:
            QMessageBox.information(self, "Camera Loaded", f"Camera {selected_camera_index} is now active.")
            
            # Start reading frames from the camera
            self.playing = True
            self.realtime_input = True
            self.timer.start(30)
            
            dialog.accept()
            
    def pause_play(self) -> None:
        """
        Pause or play the video/camera feed.

        This function is connected to the Pause/Play button in the GUI. It
        toggles the self.playing flag, which is used to control whether the
        GUI is currently updating the video feed in real-time. If the video
        capture is not open (i.e. no video or camera is loaded), it displays
        a warning message to the user.

        Returns:
            None
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
        if self.video_capture is None or not self.video_capture.isOpened():
            QMessageBox.warning(self, "No Video/Camera", "Please load a video or camera first!")
            return

        self.playing = not self.playing
<<<<<<< HEAD
=======
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.playing:
            self.timer.start(30)
        else:
            self.timer.stop()

<<<<<<< HEAD
    def display_frame(self):
=======
    def display_frame(self) -> None:
        """
        Read a frame from the video capture and update the GUI.

        This function is called at a rate of 30 frames per second by the
        QTimer. It reads a frame from the video capture, performs analysis
        on each ROI in the frame, updates the cross position of each ROI,
        and draws the ROIs and scrolling axes on the frame. Finally, it
        converts the frame to RGB and displays it in the QLabel in the GUI.

        If the video capture is not open or if a frame could not be read
        from the video capture, it stops the timer and exits the function.

        Returns:
            None
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
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
                
<<<<<<< HEAD
                
                
=======
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
<<<<<<< HEAD
            # self.video_canvas_label.setPixmap(self.current_pixmap)

            self.video_canvas_label.setPixmap(self.current_pixmap)
          
    def start_drawing_roi(self):
=======

            self.video_canvas_label.setPixmap(self.current_pixmap)
          
    def start_drawing_roi(self) -> None:
        """
        Starts drawing a new ROI.

        If the arrow direction is not locked, it will show a message box
        asking the user to confirm the direction.

        This function is called when the user clicks the "Add one ROI" button.

        Returns:
            None
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if not self.arrow_locked:
            self.message_boxes("Confirm Direction")

        self.drawing_roi = True

<<<<<<< HEAD
    def mouse_press_event(self, event):
=======
    def mouse_press_event(self, event: QMouseEvent) -> None:
        """
        Handles the mouse press event.
        
        If the user is currently drawing a new ROI,
        it sets the start position of the ROI.
        
        If the user is currently drawing a new arrow,
        it sets the start position of the arrow.
        
        The position is adjusted based on the scaling and offsets
        of the QLabel that displays the video.
        
        Parameters:
            event (QEvent): The QMouseEvent object.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.drawing_roi:
            # Adjust the start position based on scaling and offsets
            self.current_roi_start = self.adjust_mouse_position(event.pos())
            
        if self.drawing_arrow:
            self.arrow.start = self.adjust_mouse_position(event.pos())
        
<<<<<<< HEAD
    def mouse_move_event(self, event):
=======
    def mouse_move_event(self, event: QMouseEvent) -> None:
        """
        Handles the mouse move event.

        If the user is currently drawing a new ROI,
        it updates the current position of the ROI.

        If the user is currently drawing a new arrow,
        it updates the end position of the arrow.

        The position is adjusted based on the scaling and offsets
        of the QLabel that displays the video.

        Parameters:
            event (QEvent): The QMouseEvent object.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.drawing_roi and self.current_roi_start:
            # Adjust the current position while dragging
            end = self.adjust_mouse_position(event.pos())
            start = self.current_roi_start
            self.current_roi_rect = QRect(start, end)
            self.update_video_with_roi()
        
        if self.drawing_arrow:
            self.arrow.end = self.adjust_mouse_position(event.pos())
            self.update_video_with_arrow()
            
<<<<<<< HEAD
    def mouse_release_event(self, event):
        
=======
    def mouse_release_event(self, event: QMouseEvent) -> None:
        """
        Handles the mouse release event.

        If the user is currently drawing a new ROI,
        it adds the new ROI to the list if it is valid.

        If the user is currently drawing a new arrow,
        it updates the arrow's end position,
        calculates the overflow direction angle,
        and updates the video with the new arrow.

        Parameters:
            event (QEvent): The QMouseEvent object.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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

<<<<<<< HEAD
    def adjust_mouse_position(self, pos):
        """
        Adjust the mouse position relative to the displayed video frame.
        """
=======
    def adjust_mouse_position(self, pos: QPoint) -> QPoint:
        """
        Adjusts the given mouse position relative to the displayed video frame.

        This function accounts for any scaling differences between the current
        pixmap and the QLabel displaying it, adjusting the input position
        accordingly. If no pixmap is currently set, the input position is returned
        unchanged.

        Parameters:
            pos (QPoint): The original mouse position to be adjusted.

        Returns:
            QPoint: The adjusted mouse position considering any scaling offsets.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
    
<<<<<<< HEAD
    def update_overflow_direction_textbox(self):
=======
    def update_overflow_direction_textbox(self) -> None:
        """
        Updates the overflow direction textbox based on the current arrow direction.

        If the arrow direction is locked, a message box is shown. Otherwise, the
        textbox is updated with the current angle in degrees.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.arrow_locked:
            self.message_boxes("Arrow Locked")
            return
        
        if self.arrow:
            self.arrow_angle = self.arrow.angle
            self.direction_textbox.setText(f"{np.degrees(self.arrow_angle):.2f}")
            
<<<<<<< HEAD
    def update_video_with_roi(self):
=======
    def update_video_with_roi(self) -> None:
        """
        Overlay the currently drawn Region Of Interest (ROI) on the video frame.

        This function draws the rectangle representing the ROI being drawn
        on top of the current video frame pixmap. The updated pixmap is then
        set to the video display label for real-time visual feedback.

        Preconditions:
            - self.current_pixmap is a valid QPixmap representing the current video frame.
            - self.current_roi_rect is a valid QRect representing the ROI being drawn.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        # Overlay the drawing ROI on the current video frame
        if self.current_pixmap and self.current_roi_rect:
            temp_pixmap = self.current_pixmap.copy()
            painter = QPainter(temp_pixmap)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.current_roi_rect)
            painter.end()
            self.video_canvas_label.setPixmap(temp_pixmap)

<<<<<<< HEAD
    def update_video_with_arrow(self):
        """
        Overlay the arrow on the video canvas.
        """
=======
    def update_video_with_arrow(self) -> None:
        """
        Overlays the currently drawn arrow on the video frame.

        This function draws the arrow line and arrowhead on top of the current
        video frame pixmap. The updated pixmap is then set to the video display
        label for real-time visual feedback.

        Preconditions:
            - self.current_pixmap is a valid QPixmap representing the current video frame.
            - self.arrow is a valid Arrow instance representing the drawn arrow.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.current_pixmap and self.arrow and self.arrow.start and self.arrow.end:
            temp_pixmap = self.current_pixmap.copy()
            painter = QPainter(temp_pixmap)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
<<<<<<< HEAD
            # Draw the arrow line
            painter.drawLine(self.arrow.start, self.arrow.end)
=======
            
            # Draw the arrow line
            painter.drawLine(self.arrow.start, self.arrow.end)
            
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            # Draw arrowhead
            dx = self.arrow.end.x() - self.arrow.start.x()
            dy = self.arrow.end.y() - self.arrow.start.y()
            angle = np.arctan2(-dy, dx)
            length = 10  # Length of arrowhead lines
<<<<<<< HEAD
=======
            
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            x1 = self.arrow.end.x() - length * np.cos(angle - np.pi / 6)
            y1 = self.arrow.end.y() + length * np.sin(angle - np.pi / 6)
            x2 = self.arrow.end.x() - length * np.cos(angle + np.pi / 6)
            y2 = self.arrow.end.y() + length * np.sin(angle + np.pi / 6)
<<<<<<< HEAD
            painter.drawLine(self.arrow.end, QPoint(int(x1), int(y1)))
            painter.drawLine(self.arrow.end, QPoint(int(x2), int(y2)))
            painter.end()
            self.video_canvas_label.setPixmap(temp_pixmap)

    def manual_arrow_angle_update(self):
        """
        Update the arrow direction based on the value entered in the textbox.
        """
=======
            
            painter.drawLine(self.arrow.end, QPoint(int(x1), int(y1)))
            painter.drawLine(self.arrow.end, QPoint(int(x2), int(y2)))
            painter.end()
            
            self.video_canvas_label.setPixmap(temp_pixmap)

    def manual_arrow_angle_update(self) -> None:
        """
        Updates the arrow direction based on the value entered in the textbox.

        Called when the user enters a new value in the textbox and presses Enter.
        Parses the user input as a float and updates the arrow angle.
        If the input is invalid (e.g. not a number), shows a warning message.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        try:
            # Parse the user input and update the arrow angle
            self.arrow_angle = np.radians(float(self.direction_textbox.text()))
            QMessageBox.information(self, "Direction Updated", f"Overflow direction set to {np.degrees(self.arrow_angle):.2f}°.")
<<<<<<< HEAD
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value for the overflow direction.")

    def asking_lock_arrow_direction(self):
=======
        
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value for the overflow direction.")

    def asking_lock_arrow_direction(self) -> None:
        """
        Asks the user if they want to lock the arrow direction.

        If the user has not yet confirmed the arrow direction, shows a message box
        asking the user to confirm the direction. If the user has already confirmed
        the direction, shows a message box saying that the direction is already locked.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.arrow_locked:
            self.message_boxes("Arrow Locked")
            return
            
        self.message_boxes("Confirm Direction")
         
<<<<<<< HEAD
    def lock_arrow_direction(self):
        """
        Lock the arrow direction, preventing further modifications.
        """
=======
    def lock_arrow_direction(self) -> None:
        """
        Locks the overflow direction.

        Called when the user clicks the "Lock Direction" button. Parses the user input
        as a float and updates the arrow angle. If the input is invalid (e.g. not a number),
        shows a warning message. After locking the direction, the arrow is updated to
        reflect the new direction. The overflow direction is also saved to the auto-save file.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        try:
            # Parse angle from the textbox
            self.arrow_angle = np.radians(float(self.direction_textbox.text()))
            self.arrow_locked = True
            self.arrow.angle = self.arrow_angle
            self.arrow.set_displaying_preset(self.video_canvas_label)
            self.arrow.update_arrow_canvas()
            self.auto_saver.update_arrow_direction(self.arrow_angle)
            QMessageBox.information(self, "Direction Locked", f"Overflow direction locked at {np.degrees(self.arrow_angle):.2f}°.")
<<<<<<< HEAD
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
        
=======
        
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value for the overflow direction.")

    def fps_calculation(self) -> None:
        
        """
        Calculates the FPS of the input video.

        If the input is not a real-time input, simply reads the FPS from the video capture.
        Otherwise, calculates the FPS by reading a fixed number of frames and measuring the time taken.
        """
        
        if not self.realtime_input:
            self.fps_recording = self.video_capture.get(cv2.CAP_PROP_FPS)
            print("FPS of input video is:", self.fps_recording)
            return
        
        self.start_record_button.setText("Calculating FPS...")
        self.start_record_button.setStyleSheet("background-color: green; color: white;")
        self.start_record_button.clicked.disconnect(self.start_recording)
        QApplication.processEvents()
                        
        num_frames = 30
        start_time = time.time()
        print(start_time)
        
        for i in range(num_frames):
            ret, frame = self.video_capture.read()

        end_time = time.time()
        print(end_time)
        elapsed_time = end_time - start_time
        self.fps_recording = num_frames / elapsed_time
    
    def start_recording(self) -> None:
        """
        Initiates video recording if an active video feed is available and recording is enabled.

        This function checks if the video feed is active and if recording settings are properly configured.
        If the frames per second (FPS) for recording is not calculated, it calculates the FPS.
        If recording is enabled in the export settings, it creates a VideoRecorder instance and starts
        recording the video to the specified directory with the given filename. The UI is updated to 
        indicate that recording has started.

        If there is no active video feed, or recording is disabled, it displays a warning message.

        Preconditions:
            - An active video feed must be available.
            - Recording settings must be configured in the export settings.

        Returns:
            None
        """
    
        if not self.video_capture or not self.video_capture.isOpened():
            QMessageBox.warning(self, "Warning", "No active video feed to record.")
            return
        
        if self.fps_recording == 0:
            self.fps_calculation()
                
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if self.export.video_directory and self.export.record_video:
            
            file_path = self.export.video_directory
            file_name = self.export.video_filename
            
<<<<<<< HEAD
            self.video_writer = VideoRecorder(file_path, file_name, frame_size = self.frame_size)
=======
            print("FPS of the video:", self.fps_recording)
            self.video_writer = VideoRecorder(file_path, file_name, frame_size = self.frame_size, fps = self.fps_recording)
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            self.video_writer.start_recording()
            self.recording = True
            
            self.start_record_button.setText("Stop Recording")
            self.start_record_button.setStyleSheet("background-color: red; color: white;")
<<<<<<< HEAD
            self.start_record_button.clicked.disconnect(self.start_recording)
=======
            # self.start_record_button.clicked.disconnect(self.start_recording)
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            self.start_record_button.clicked.connect(self.stop_recording)
        
        else:
            QMessageBox.warning(self, "Warning", "Recording is disabled.\nPlease enable it in the export settings.")
            return
        
<<<<<<< HEAD
    def stop_recording(self):
=======
    def stop_recording(self) -> None:
        """
        Stops the video recording and saves the recorded video.

        This function stops the video recording and sets the recording flag to False.
        It also updates the UI to indicate that recording has stopped.
        Finally, it displays a message box to inform the user that the video has been saved.

        Preconditions:
            - The video recording must have been started by calling the start_recording method.
            - The video recording must not have been stopped already.

        Returns:
            None
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
    
<<<<<<< HEAD
    def auto_save(self, roi, roi_index):
=======
    def auto_save(self, 
                  roi: ROI, 
                  roi_index: int) -> None:
        """
        Automatically saves the most recent velocity and timestamp data for a given region of interest (ROI).

        This function retrieves the latest velocity and timestamp from the ROI's analysis module,
        along with the current frame index, and saves this data using the auto_saver.
        
        Parameters:
            roi (object): The region of interest containing the analysis module with velocity history.
            roi_index (int): The index of the ROI for which the data is being saved.

        Preconditions:
            - The ROI's analysis module must contain a non-empty velocity history.
            - The auto_saver must be properly initialized and configured to store frame data.

        Returns:
            None
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        velocity = roi.analysis_module.velocity_history[-1]["velocity"]
        timestamp = roi.analysis_module.velocity_history[-1]["timestamp"]
        frame_index = roi.analysis_module.get_frame_count()
        
        self.auto_saver.add_frame_data(roi_index, frame_index, velocity, timestamp)
    
<<<<<<< HEAD
    def close_event(self, event):
=======
    def close_event(self, 
                    event: QCloseEvent) -> None:
        
        """
        Override of the QWidget closeEvent method.

        Called when the main window is closed. If a video recording is in progress,
        it releases the VideoRecorder and stops the recording. Then, it calls the
        base class implementation to close the window.

        Parameters:
            event (QCloseEvent): A QCloseEvent object.

        Returns:
            None
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
        if self.video_writer:
            self.video_writer.release()
        super().closeEvent(event)
      
<<<<<<< HEAD
    def save(self):
        try:
=======
    def save(self) -> None:
        """
        Saves the current state of the application by exporting analysis results and stopping video playback.
        
        This function performs the following steps:
        
        1. Exports analysis results to the configured directory and filename.
        2. Stops video playback by stopping the timer and releasing the video capture object.
        3. Notifies the user of success with a message box.
        4. Resets the application state by calling the reset_application method.
        
        If an error occurs during the save process, the function shows a critical error message box with the error message.
        
        Returns:
            None
        """
        
        try:
            
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            # Step 1: Save analysis results
            if not self.export.export_directory or not self.export.export_filename:
                QMessageBox.warning(self, "Export Error", "Please configure export settings before saving.")
                return
<<<<<<< HEAD

=======
            
            # Step 2: Export analysis results
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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

<<<<<<< HEAD
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
=======
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"An error occurred while saving data: {e}")

    def export_data(self) -> None:
        """
        Exports the current analysis results using the Export class.

        This function triggers the export of data, including ROIs and arrow angles,
        to the configured directory and filename using the excel_resutls method.

        Returns:
            None
        """
        self.export.excel_resutls(self.rois, self.arrow_angle)

    def reset_application(self) -> None:
        """
        Resets the application to its initial state.

        This function is called when the "Reset Application" button is clicked.
        It clears all analysis results, resets the video playback state,
        resets the arrow drawing, and resets the export settings to their default state.
        It also displays a message box to inform the user that the application has been reset.

        Returns:
            None
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        self.rois = []
        self.movement_buffers = {}
        self.movement_curves = {}
        self.plot_widget.clear()
        self.video_canvas_label.clear()
        
<<<<<<< HEAD
=======
        self.playing = False
        self.realtime_input = False
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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

