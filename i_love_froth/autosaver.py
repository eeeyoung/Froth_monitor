import json
import os

from datetime import datetime

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
    
    def add_frame_data(self, roi_index, frame_index, velocity, timestamp):
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
