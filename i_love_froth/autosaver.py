<<<<<<< HEAD
import json
import os

from datetime import datetime

class AutoSaver:
    def __init__(self, 
                 file_path = "data/auto_save",
                 file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")):
=======
"""AutoSaver Module for Froth Tracker Application.

This module defines the `AutoSaver` class, which provides functionality for
automatic saving and loading of application data. It is designed to persist
analysis results, including arrow direction and movement data for multiple
regions of interest (ROIs), into a JSON file.

Classes:
--------
AutoSaver
    Handles automatic saving and loading of application state to/from a JSON file.
    
Imports:
--------
- json:
    For serializing and deserializing application data.
- os:
    For checking file existence and constructing file paths.
- datetime:
    For generating timestamped file names for autosaving.
"""

import json
import os
from datetime import datetime

class AutoSaver:
    """
    AutoSaver Class for Managing Automatic Data Persistence.

    The `AutoSaver` class provides methods to automatically save and load
    analysis data, such as arrow directions and movement data for regions
    of interest (ROIs). The data is saved in JSON format to a file, ensuring
    that the application's state is preserved even in the event of a crash.

    Attributes:
    ----------
    file_path : str
        The full file path for the autosave file, including directory and filename.
    data : dict
        The data structure used to store the application state, including:
        - `arrow_direction`: The angle of the overflow direction (in radians).
        - `roi_data`: A list of dictionaries, each containing ROI movement data.

    Methods:
    -------
    __init__(file_path: str = "data/auto_save", file_name: str = None) -> None
        Initializes the AutoSaver instance with a default file path and filename.
    update_arrow_direction(arrow_angle: float) -> None
        Updates the arrow direction in the autosave data with the given angle.
    add_frame_data(roi_index: int, frame_index: int, velocity: float, timestamp: str) -> None
        Adds frame-level movement data to the autosave data for a specified ROI.
    save_to_file() -> None
        Saves the current autosave data to the file in JSON format.
    load_from_file() -> dict
        Loads previously saved data from the file and returns it as a dictionary.
    """
    
    def __init__(self, 
                 file_path: str = "data/auto_save",
                 file_name: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
        self.file_path = f"{file_path}/{file_name}.json"
        self.data = {
            "arrow_direction": None,
            "roi_data": []
        }
    
<<<<<<< HEAD
    def update_arrow_direction(self, arrow_angle):
        self.data["arrow_direction"] = float(arrow_angle)  # Store as float
    
    def add_frame_data(self, roi_index, frame_index, velocity, timestamp):
=======
    def update_arrow_direction(self, 
                               arrow_angle: float) -> None:
        """
        Updates the overflow direction to the given angle (in radians) in the autosave data.

        The angle is stored as a float in the autosave data.
        """
        
        self.data["arrow_direction"] = float(arrow_angle)  # Store as float
    
    def add_frame_data(self, 
                       roi_index: int, 
                       frame_index: int, 
                       velocity: float, 
                       timestamp: str) -> None:
        """
        Adds frame data to the given ROI index.

        The ROI index is 0-indexed, meaning the first ROI is at index 0.

        The frame index is the index of the frame in the video.

        The velocity is the detected velocity of the movement in the frame.

        The timestamp is a string representing the time that the frame was detected.

        The data is appended to the existing movement data for the given ROI.

        The data is saved to the autosave file after adding.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        # Ensure the ROI exists
        while len(self.data["roi_data"]) <= roi_index:
            self.data["roi_data"].append({"ROI Index": len(self.data["roi_data"]) + 1, "Movement Data": []})

        velocity = float(velocity)
        roi_index = int(roi_index)
        frame_index = int(frame_index)
        
        # Append movement data
        self.data["roi_data"][roi_index]["Movement Data"].append({
            "Frame Index": frame_index,
            "Velocity": velocity,
            "Timestamp": timestamp,
        })
        self.save_to_file()  # Save every update
    
<<<<<<< HEAD
    def save_to_file(self):
=======
    def save_to_file(self) -> None:
        """
        Saves the autosave data to the file path specified during initialization.

        If a serialization error occurs, a TypeError is raised, and the problematic data is printed.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.data, f, indent=4)
        except TypeError as e:
            print(f"Serialization error: {e}")
            print(f"Problematic data: {self.data}")
            raise
    
<<<<<<< HEAD
    def load_from_file(self):
=======
    def load_from_file(self) -> dict:
        
        """
        Loads autosave data from the file specified during initialization.

        If the file does not exist, returns None.

        Otherwise, loads the JSON data from the file and returns it.

        The loaded data is stored in the 'data' attribute of the AutoSaver instance.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
                return self.data
<<<<<<< HEAD
=======
            
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        return None        
