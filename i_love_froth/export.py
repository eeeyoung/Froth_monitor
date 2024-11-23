from PySide6.QtWidgets import (QPushButton, QLabel, QFileDialog, 
                               QVBoxLayout, QMessageBox, QDialog, QLineEdit, QCheckBox,
                               QHBoxLayout, QFileDialog, QRadioButton, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import numpy as np
from datetime import datetime
from openpyxl import Workbook


class Export:
    def __init__(self, parent=None):
        self.parent = parent
        self.export_directory = ""
        self.video_directory = ""
        self.export_filename = datetime.now().strftime("%Y%m%d")
        self.video_filename = datetime.now().strftime("%Y%m%d")
        self.velocity_sum = 0.0
        
        self.save_video_in_same_dir = True
        self.record_video = True
        
        self.font_big = QFont("Arial", 13)
        self.font_small = QFont("Arial", 12)
       

    def export_setting_window(self):
        """
        Opens a dialog for configuring export settings.
        """
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Export Settings")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Export Directory Selection
        directory_label = QLabel("Data Export Directory:", dialog)
        directory_label.setFont(self.font_big)
        layout.addWidget(directory_label)
        

        directory_button = QPushButton("Select Data Directory", dialog)
        directory_button.clicked.connect(lambda: self.select_data_directory(dialog))
        layout.addWidget(directory_button)

        # Add QLabel to display the selected directory and set an object name
        directory_display = QLabel(self.export_directory if self.export_directory else "Not selected", dialog)
        directory_display.setObjectName("directory_display")  # Assign a unique name for findChild
        layout.addWidget(directory_display)

        # Export Filename Input
        filename_label = QLabel("Export Filename (without extension):", dialog)
        filename_label.setFont(self.font_big)
        layout.addWidget(filename_label)

        filename_input = QLineEdit(self.export_filename, dialog)
        layout.addWidget(filename_input)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)  # Horizontal line
        separator.setFrameShadow(QFrame.Sunken)  # Sunken style
        layout.addWidget(separator)

        self.add_video_selection_section(layout, dialog)

        # Save Button
        save_button = QPushButton("Save Settings", dialog)
        save_button.clicked.connect(lambda: self.save_export_settings(dialog, filename_input))
        layout.addWidget(save_button)

        dialog.exec()

    def add_video_selection_section(self, layout, dialog):
        
        def update_ui():
            """
            Update the UI based on whether the user selected to save the video in the same directory.
            
            If the user selected "Yes", hide the additional options.
            If the user selected "No", show the additional options and set the "Record Video" checkbox to the current value of self.record_video.
            """
            is_same_dir = yes_radio.isChecked()
            self.save_video_in_same_dir = is_same_dir
            no_radio.setChecked(not is_same_dir)

            print("is_same_dir:", is_same_dir)
            # Show or hide additional options if "No" is selected
            recording_video_checkbox.setVisible(not is_same_dir)
            
            if not is_same_dir:
                
                recording_video_checkbox.setChecked(self.record_video)
                recording_video_directory_button.setVisible(self.record_video)
                recording_video_directory_display.setVisible(self.record_video)

        def on_radio_selection():
            """
            Handle the event when a radio button is selected.

            If the "Yes" radio button is selected, set save_video_in_same_dir to True.
            If the "No" radio button is selected, set save_video_in_same_dir to False.
            After updating the selection state, invoke the update_ui function to refresh the UI based on the new selection.
            """
            if yes_radio.isChecked():

                self.save_video_in_same_dir = True
                self.record_video = True
                
            elif no_radio.isChecked():
                self.record_video = False
                self.save_video_in_same_dir = False
            update_ui()

        # Save Recording Video Options
        video_label = QLabel("Would you like to save the recording video in the same directory?")
        video_label.setFont(self.font_big)
        layout.addWidget(video_label)

        # Create radio buttons
        yes_radio = QRadioButton("Yes (Enable video recording)")
        no_radio = QRadioButton("No")
        video_radio_layout = QHBoxLayout()
        video_radio_layout.addWidget(yes_radio)
        video_radio_layout.addWidget(no_radio)
        layout.addLayout(video_radio_layout)
        
        # Set initial state
        if self.save_video_in_same_dir:
            yes_radio.setChecked(True)
        else:
            no_radio.setChecked(True)

        # Connect signals to the slots
        yes_radio.toggled.connect(on_radio_selection)
        no_radio.toggled.connect(on_radio_selection)
        
        recording_video_checkbox = QCheckBox("Tick me to preset video recording \n(otherwise video recording will be disabled in this mission)", dialog)
        recording_video_directory_button = QPushButton("Set Recording Directory")
        recording_video_directory_display = QLabel("Not selected", dialog)
        recording_video_directory_display.setObjectName("recording_video_directory_display")

        recording_video_checkbox.setVisible(False)
        recording_video_directory_button.setVisible(False)
        recording_video_directory_display.setVisible(False)

        layout.addWidget(recording_video_checkbox)
        layout.addWidget(recording_video_directory_button)
        layout.addWidget(recording_video_directory_display)

        recording_video_checkbox.stateChanged.connect(
            lambda: self.enable_video_recording(recording_video_checkbox.isChecked())
        )
        recording_video_checkbox.stateChanged.connect(
            lambda: recording_video_directory_button.setVisible(recording_video_checkbox.isChecked())
        )
        recording_video_checkbox.stateChanged.connect(
            lambda: recording_video_directory_display.setVisible(recording_video_checkbox.isChecked())
        )
        recording_video_directory_button.clicked.connect(lambda: self.select_video_directory(dialog))
              
        video_filename_label = QLabel("Video Filename (without extension):", dialog)
        video_filename_label.setFont(self.font_big)
        layout.addWidget(video_filename_label)

        video_filename_input = QLineEdit(self.export_filename, dialog)
        video_filename_input.setObjectName("video_filename_input")
        layout.addWidget(video_filename_input)
    
    def enable_video_recording(self, if_record_video):
        self.record_video = if_record_video
        print(self.record_video)
        
    def select_video_directory(self, parent_dialog):
        directory = QFileDialog.getExistingDirectory(self.parent, "Select Recording Saving Directory")
        
        if directory:
            self.video_directory = directory
            # Update directory label in the parent dialog
            directory_display = parent_dialog.findChild(QLabel, "recording_video_directory_display")
            self.record_video = True
            if directory_display:  # Ensure the QLabel is found
                print(self.video_directory)
                directory_display.setText(self.video_directory)

    def select_data_directory(self, parent_dialog):
        """
        Opens a file dialog to select the export directory.
        """
        directory = QFileDialog.getExistingDirectory(self.parent, "Select Data Saving Directory")
        
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
        
        video_filename_input = dialog.findChild(QLineEdit, "video_filename_input")
        self.video_filename = video_filename_input.text()
        
        # Display a warning if the directory is not set
        if not self.export_directory:
            QMessageBox.warning(self.parent, "Warning", "Data Export directory is not set.")
            return
        
        if self.save_video_in_same_dir and self.record_video:
            self.video_directory = self.export_directory
        
        # Display a warning if the directory is not set
        if not self.video_directory and self.record_video:
            QMessageBox.warning(self.parent, "Warning", "Recoroding Export directory is not set.")
            return
        
        # Display a success message
        if not self.record_video:
            QMessageBox.information(
                self.parent,
                "Settings Saved",
                f"Data export settings saved:\nDirectory: {self.export_directory}\nFilename: {self.export_filename}\
                \n\n\n Recording function is disabled"
            )
        
        else:
            QMessageBox.information(
                self.parent,
                "Settings Saved",
                f"Data export settings saved:\nDirectory: {self.export_directory}\nFilename: {self.export_filename}\
                \n\n\nRecording export settings saved:\nDirectory: {self.video_directory}\nFilename: {self.video_filename}"
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
            
            frame_count = 0
            
            for frame_index, frame_data in enumerate(roi.analysis_module.get_results()):
                velocity = frame_data["velocity"]
                timestamp = frame_data["timestamp"]
                
                print("frame_index", frame_index + 1)
                print("delta", velocity)
                print("timestamp", timestamp)
                
                average_velocity, frame_count = self.get_average_velocity(velocity, frame_count, timestamp)
                
                roi_data["Movement Data"].append({
                    "Frame Index": frame_index + 1,
                    "Velocity": velocity,
                    "Timestamp": timestamp,
                    "Average Velocity": average_velocity,
                })
                
            data["roi_data"].append(roi_data)
            
        print(data)
        return data
    
    def get_average_velocity(self, velocity, frame_count, timestamp):
        
        if frame_count == 0:
            self.velocity_sum = 0
            
        frame_count += 1
        self.velocity_sum += velocity
        
        if frame_count == 1:
            self.start_time = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S.%f")
            
            
        if frame_count == 15:
            self.end_time = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S.%f")
            time_diff_temp = self.end_time - self.start_time
            time_diff = time_diff_temp.total_seconds()
            average_velocity = self.velocity_sum / time_diff
            return average_velocity, 0
        
        else:
            return None, frame_count
        
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
            ws.append(["Frame Index", 
                       "Velocity(pixels/frame)",
                       "Timestamp",
                       "Average Velocity(pixels/seconds)"
                       ])

            # Add movement data
            for movement in roi["Movement Data"]:
                ws.append([movement["Frame Index"], 
                           movement["Velocity"],
                           movement["Timestamp"],
                           movement["Average Velocity"]
                           ])

        # Save the workbook
        wb.save(file_path)

