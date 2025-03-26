"""Video Analysis Module for Froth Tracker Application.

This module defines the `VideoAnalysisModule` class, which provides methods
for analyzing video frames using optical flow to calculate motion in a
specific direction. It supports calculating velocities, storing motion
history, and generating timestamps for each frame.

Classes:
--------
VideoAnalysisModule
    Provides functionality to process video frames and calculate motion
    velocities based on dense optical flow.

Imports:
--------
- cv2: For video frame processing and optical flow calculations.
- numpy: For mathematical operations and averaging flow data.
- random: For generating random colors for visualization.
- datetime: For timestamp generation.

Example Usage:
--------------
To use the module, instantiate the `VideoAnalysisModule` class with the
desired scrolling axis directions (`arrow_dir_x` and `arrow_dir_y`), and
call the `analyze` method on each video frame. Use `get_results` to retrieve
the velocity history.
"""

import cv2
import numpy as np
import random
from datetime import datetime

class VideoAnalysis:
    """
    Video Analysis Class for Motion Detection and Analysis.

    The `VideoAnalysisModule` class processes video frames to calculate
    motion velocities in a specific direction using dense optical flow.
    It stores velocity history, generates timestamps for each frame, and
    calculates motion relative to a specified scrolling axis.

    Attributes:
    ----------
    previous_frame : np.ndarray
        The last processed frame for motion analysis.
    velocity_history : list
        Stores the history of motion velocities and timestamps for each frame.
    color : tuple[int, int, int]
        A random RGB color for visualizing motion.
    current_velocity : float
        The most recent velocity calculated in the direction of the scrolling axis.
    arrow_dir_x : float
        The x component of the scrolling axis direction.
    arrow_dir_y : float
        The y component of the scrolling axis direction.

    Methods:
    -------
    __init__(arrow_dir_x: float, arrow_dir_y: float) -> None
        Initializes the VideoAnalysisModule with the given scrolling axis direction.
    analyze(current_frame: np.ndarray) -> tuple[float, float]
        Processes the current frame to calculate motion velocities using dense optical flow.
    get_current_velocity(avg_flow_x: float, avg_flow_y: float) -> float
        Calculates the velocity in the scrolling axis direction.
    get_current_time() -> str
        Returns the current timestamp in the format "dd/mm/yyyy HH:MM:SS.sss".
    get_frame_count() -> int
        Returns the total number of frames processed.
    get_results() -> list
        Retrieves the history of velocities and timestamps for all processed frames.
    generate_random_color() -> tuple[int, int, int]
        Generates a random RGB color.
    """
    
    def __init__(self, 
                 arrow_dir_x: float, 
                 arrow_dir_y: float) -> None:
        """
        Initialize the VideoAnalysisModule with the given direction for the scrolling axis.
        
        Parameters
        ----------
        arrow_dir_x : float
            The x direction for the scrolling axis (positive is right, negative is left).
        arrow_dir_y : float
            The y direction for the scrolling axis (positive is down, negative is up).
        """
        
        self.previous_frame = None  # Store the previous frame for motion analysis
        self.velocity_history = []  # Store delta pixel values between frames
        self.color = self.generate_random_color()
        self.current_velocity = 0
        self.arrow_dir_x = arrow_dir_x
        self.arrow_dir_y = arrow_dir_y
        
    def analyze(self, 
                current_frame: np.ndarray) -> tuple[float, float]:
        """
        Analyze the given frame for changes in x and y directions by calculating dense optical flow using the Farneback method.
        
        Parameters
        ----------
        current_frame : np.ndarray
            The frame to analyze.
        
        Returns
        -------
        tuple[float, float]
            The delta pixel values in x and y directions between the current and previous frames.
        """
        
        # Analyze the given frame for changes in x and y directions
        if self.previous_frame is None:
            # If there's no previous frame, store the current frame and return
            self.previous_frame = current_frame
            return None, None

        # Convert both current and previous frames to grayscale
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_previous = cv2.cvtColor(self.previous_frame, cv2.COLOR_BGR2GRAY)

        # Calculate dense optical flow using Farneback method
        flow = cv2.calcOpticalFlowFarneback(gray_previous, gray_current, None, 0.5, 3, 25, 3, 7, 1.5, 0)

        # Extract flow components in x and y directions
        flow_x = flow[..., 0]
        flow_y = flow[..., 1]

        avg_flow_x = np.mean(flow_x)
        avg_flow_y = np.mean(flow_y)
        
        # Store the delta pixel values between the current and previous frame
        
        self.velocity_history.append({
            "velocity": self.get_current_velocity(avg_flow_x, avg_flow_y),
            "timestamp": self.get_current_time(),
        })
        
        # Update the previous frame to the current frame for the next analysis
        self.previous_frame = current_frame 
        
        # Return delta pixel values for the current frame
        return avg_flow_x, avg_flow_y

    def get_current_velocity(self, 
                             avg_flow_x: float, 
                             avg_flow_y: float) -> float:
        """
        Calculate the current velocity in the direction of the scrolling axis.

        Parameters
        ----------
        avg_flow_x : float
            The average flow in the x direction.
        avg_flow_y : float
            The average flow in the y direction.

        Returns
        -------
        float
            The current velocity in the direction of the scrolling axis.
        """
        self.current_velocity: float = avg_flow_x * self.arrow_dir_x + avg_flow_y * self.arrow_dir_y
        return self.current_velocity
    
    def get_current_time(self) -> str:
        """
        Return the current time in the format dd/mm/yyyy HH:MM:SS.sss.

        Returns
        -------
        str
            The current time as a string.
        """
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
        
    def get_frame_count(self) -> int:
        """
        Return the number of frames processed and stored in the velocity history.

        Returns
        -------
        int
            The number of frames processed.
        """
        return len(self.velocity_history)
        
    def get_results(self) -> list: 
        """
        Return all stored delta pixel results.

        Returns
        -------
        list
            A list of dictionaries containing the velocity and timestamp
            for each frame processed.
        """
        
        # Return all stored delta pixel results
        return self.velocity_history

    def generate_random_color(self) -> tuple[int, int, int]:
        """
        Generate a random color in RGB format.
        """
        
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)  # Return as an RGB tuple
    
if __name__ == "__main__":
    # Example usage of VideoAnalysisModule
    video_analysis = VideoAnalysis()

    # Capture video from file path
    video_path = "data/input_videos/test.avi"  # Replace with the actual path to your video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Analyze the current frame
        delta_x, delta_y = video_analysis.analyze(frame)
        if delta_x is not None and delta_y is not None:
            print(f"Delta X: {np.mean(delta_x)}, Delta Y: {np.mean(delta_y)}")

        # Display the current frame
        cv2.imshow('Video Frame', frame)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
