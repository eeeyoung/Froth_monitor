"""Video Recording Module for Froth Tracker Application.

This module defines the `VideoRecorder` class, which is responsible for recording video frames
and saving them to a file. The class provides methods to start, write, and stop video recording,
allowing seamless integration with real-time video analysis workflows.

Classes:
--------
VideoRecorder
    Handles video recording operations, including initializing a video writer,
    writing frames to the video file, and managing recording state.

Imports:
--------
- cv2 (OpenCV): For video writing operations.
- numpy (optional for frame type): For representing video frames as arrays.

Example Usage:
--------------
To use the module, instantiate the `VideoRecorder` class with the desired settings,
start recording, write frames, and stop recording when done.
"""

import numpy as np
import cv2

class VideoRecorder:
    """
    Video Recorder Class.

    The `VideoRecorder` class handles video recording tasks, including initializing a video writer,
    writing video frames to a file, and managing the recording state. It supports configurable
    output file paths, frame rates, and frame sizes.

    Attributes:
    ----------
    temp_file_path : str
        Temporary directory path for storing the video file during recording.
    file_name : str
        Name of the video file without extension.
    recording : bool
        Indicates whether the recorder is currently recording.
    writer : cv2.VideoWriter
        The OpenCV video writer object used for recording.
    file_path : str
        Full path to the video file being recorded.
    fps : int
        Frame rate (frames per second) for the recording.
    frame_size : tuple
        Dimensions (width, height) of the video frames.
    frame_count : int
        Counter for the number of frames recorded.
    frame_1_time : float
        Timestamp of the first recorded frame.
    frame_2_time : float
        Timestamp of the second recorded frame.

    Methods:
    -------
    start_recording() -> None
        Starts recording video to a file. Initializes the video writer.
    write_frame(frame: np.ndarray) -> None
        Writes a single frame to the video file.
    stop_recording() -> None
        Stops recording and releases resources.
    is_recording() -> bool
        Checks if the recorder is currently recording.
    """
    
    def __init__(self, 
                 file_path: str = "", 
                 file_name: str = "./recording", 
                 fps: int = 30, 
                 frame_size: tuple = (640, 480)) -> None:
        """
        Initialize the VideoRecorder.
        
        Args:
            output_directory (str): Directory to save the video file.
            filename_prefix (str): Prefix for the video file name.
            fps (int): Frames per second for the recording.
            frame_size (tuple): Width and height of the video frames.
        """
        
        self.temp_file_path = file_path
        self.file_name = file_name

        self.recording = False
        self.writer = None
        self.file_path = None
        
        self.fps = fps
        self.frame_size = frame_size
        self.frame_count = 0
        self.frame_1_time = None
        self.frame_2_time = None
        
    def start_recording(self) -> None:
        """
        Start recording video to a file.
        """ 
        
        self.file_path = f"{self.temp_file_path}/{self.file_name}.mp4"
        self.writer = cv2.VideoWriter(
            self.file_path,
            cv2.VideoWriter_fourcc(*'XVID'),
            self.fps,
            self.frame_size
        )
        
        self.recording = True
        print(f"Recording started. Saving to {self.file_path}")
        
    def write_frame(self, frame: np.ndarray) -> None:
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

    def stop_recording(self) -> None:
        """
        Stop recording and release resources.
        """
        if self.writer:
            self.writer.release()
            self.writer = None
        self.recording = False
        print(f"Recording stopped. Video saved at {self.file_path}")

    def is_recording(self) -> bool:
        """
        Check if the recorder is currently recording.
        
        Returns:
            bool: True if recording, False otherwise.
        """
        return self.recording        
        
        