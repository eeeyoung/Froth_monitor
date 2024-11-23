import cv2
import numpy as np
import random
from datetime import datetime

class VideoAnalysisModule:
    def __init__(self, arrow_dir_x, arrow_dir_y):
        self.previous_frame = None  # Store the previous frame for motion analysis
        self.velocity_history = []  # Store delta pixel values between frames
        self.color = self.generate_random_color()
        self.current_velocity = 0
        self.arrow_dir_x = arrow_dir_x
        self.arrow_dir_y = arrow_dir_y
        
    def analyze(self, current_frame):
        
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

    def get_current_velocity(self, avg_flow_x, avg_flow_y):
        

        self.current_velocity: float = avg_flow_x * self.arrow_dir_x + avg_flow_y * self.arrow_dir_y
        return self.current_velocity
    
    def get_current_time(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
        
    def get_frame_count(self):
        return len(self.velocity_history)
        
    def get_results(self):
        # Return all stored delta pixel results
        return self.velocity_history

    def generate_random_color(self):
        """
        Generate a random color in RGB format.
        """
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)  # Return as an RGB tuple
    
if __name__ == "__main__":
    # Example usage of VideoAnalysisModule
    video_analysis = VideoAnalysisModule()

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
