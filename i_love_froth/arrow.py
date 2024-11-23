from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QPoint
import numpy as np

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
   