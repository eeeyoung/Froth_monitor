<<<<<<< HEAD
=======
"""Arrow Module for Froth Tracker Application.

This module defines the `Arrow` class, which is responsible for managing the overflow direction
arrow in the Froth Tracker application. The arrow is used to indicate the direction of flow
and is drawn dynamically on a QLabel canvas.

Classes:
--------
Arrow
    Manages the properties and visualization of an overflow direction arrow,
    including calculations for its angle and direction components.
    
Imports:
--------
- PySide6.QtWidgets:
    QLabel - For displaying the arrow canvas.
- PySide6.QtGui:
    QPixmap, QPainter, QPen - For drawing the arrow on the canvas.
- PySide6.QtCore:
    Qt, QPoint - For managing arrow positioning and alignment.
- numpy:
    For mathematical operations such as trigonometric calculations.
"""

>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QPoint
import numpy as np

class Arrow:
<<<<<<< HEAD
    def __init__(self, 
                 canvas_label: QLabel,
                 start: QPoint = None, 
                 end: QPoint = None):
=======
    """
    Arrow Class for Managing Overflow Direction in the Froth Tracker Application.

    The `Arrow` class provides methods and attributes to manage the visualization
    and properties of an overflow direction arrow. It calculates the arrow's angle
    and direction components and updates its appearance dynamically on a QLabel canvas.

    Attributes:
    ----------
    canvas_label : QLabel
        The QLabel canvas on which the arrow is drawn.
    start : QPoint or None
        Starting point of the arrow on the canvas (default: None).
    end : QPoint or None
        Ending point of the arrow on the canvas (default: None).
    angle : float
        Angle of the arrow in radians (default: 0.0).
    arrow_dir_x : float
        X-component of the arrow's direction (calculated from the angle).
    arrow_dir_y : float
        Y-component of the arrow's direction (calculated from the angle).

    Methods:
    -------
    __init__(canvas_label: QLabel, start: QPoint = None, end: QPoint = None) -> None
        Initializes the Arrow object with a canvas label and optional start/end points.
    calculate_angle() -> None
        Calculates the arrow's angle based on its start and end points.
    calculate_components_angles() -> None
        Calculates the x and y components of the arrow's direction based on its angle.
    update_arrow_canvas() -> None
        Draws the arrow on the associated QLabel canvas with the current angle and direction.
    set_displaying_preset(video_canvas_label: QLabel) -> None
        Sets up the arrow's start and end points for visualization on the video canvas.
    reset() -> None
        Resets the arrow's angle and direction components to their initial state.
    """
    
    def __init__(self, 
                 canvas_label: QLabel,
                 start: QPoint = None, 
                 end: QPoint = None) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
        
<<<<<<< HEAD
    def calculate_angle(self):
=======
    def calculate_angle(self) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        Calculate the angle of the arrow in radians relative to the horizontal.
        """
        if self.start and self.end:
            dx = self.end.x() - self.start.x()
            dy = self.end.y() - self.start.y()
            self.angle = np.arctan2(dy, dx)

<<<<<<< HEAD
    def calculate_components_angles(self):
        self.arrow_dir_x = np.cos(self.angle)
        self.arrow_dir_y = np.sin(self.angle)
    
    def update_arrow_canvas(self):
=======
    def calculate_components_angles(self) -> None:
        """
        Calculate the x and y components of the arrow direction given the angle.
        
        The x component is the cosine of the angle, and the y component is the sine of the angle.
        """
        self.arrow_dir_x = np.cos(self.angle)
        self.arrow_dir_y = np.sin(self.angle)
    
    def update_arrow_canvas(self) -> None:
        """
        Updates the arrow canvas with the current angle and direction of the arrow.
        
        The arrow is drawn on the canvas with the center of the canvas as the starting point.
        The length of the arrow is one third of the minimum size of the canvas.
        The arrowhead is drawn with a length of 10 pixels.
        The arrow is drawn with a black pen with a width of 2 pixels.
        The updated pixmap is set to the canvas_label.
        """
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        
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
<<<<<<< HEAD

=======
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        painter.end()

        # Set updated pixmap
        self.canvas_label.setPixmap(pixmap)

<<<<<<< HEAD
    def set_displaying_preset(self, video_canvas_label):
=======
    def set_displaying_preset(self, 
                              video_canvas_label: QLabel) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
            """
            Sets up the arrow's start and end points based on the current angle for the video canvas.
            :param video_canvas_label: The QLabel representing the video canvas.
            """
<<<<<<< HEAD
=======
            
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
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
    
<<<<<<< HEAD
    def reset(self):
=======
    def reset(self) -> None:
        """
        Resets the arrow's angle and direction components to their initial state.

        This method sets the angle to 0.0 radians and both the x and y components
        of the arrow direction to 0.0, effectively resetting any direction or angle
        calculations.
        """
        
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        self.angle = 0.0    # Angle of the arrow (in radians)
        self.arrow_dir_x = 0.0
        self.arrow_dir_y = 0.0
   