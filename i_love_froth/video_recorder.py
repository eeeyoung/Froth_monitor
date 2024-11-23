import cv2
from datetime import datetime


class VideoRecorder:
    def __init__(self, file_path = "", file_name="./recording", fps=30, frame_size=(640, 480)):
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
        self.temp_file_path = file_path
        self.file_name = file_name
        self.fps = fps
        self.frame_size = frame_size
        self.recording = False
        self.writer = None
        self.file_path = None

    def start_recording(self):
        """
        Start recording video to a file.
        """
        # if not os.path.exists(self.output_directory):
        #     os.makedirs(self.output_directory)

        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.file_path = f"{self.temp_file_path}/{self.file_name}.mp4"
        
        # self.file_path = f"{self.file_name}.mp4"

        self.writer = cv2.VideoWriter(
            self.file_path,
            cv2.VideoWriter_fourcc(*'XVID'),
            self.fps,
            self.frame_size
        )
        
        self.recording = True
        print(f"Recording started. Saving to {self.file_path}")

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
        print(f"Recording stopped. Video saved at {self.file_path}")

    def is_recording(self):
        """
        Check if the recorder is currently recording.
        
        Returns:
            bool: True if recording, False otherwise.
        """
        return self.recording        
        
        