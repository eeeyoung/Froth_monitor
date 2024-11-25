<<<<<<< HEAD
from PySide6.QtCore import QRect, QPoint
import pyqtgraph as pg
import cv2
from .image_analysis import VideoAnalysisModule

class ROI:
    def __init__(self, 
                 rect: QRect, 
                 arrow_dir_x: float, 
                 arrow_dir_y: float):
        self.rect = rect
        self.analysis_module = VideoAnalysisModule(arrow_dir_x,
                                                   arrow_dir_y)
        self.cross_position = QPoint(rect.center().x(), rect.center().y())  # Initialize cross at ROI center

    def update_cross_position(self, avg_flow_x, avg_flow_y):
=======
"""Region of Interest (ROI) Module for Froth Tracker Application.

This module defines the `ROI` class, which represents a region of interest (ROI)
within a video frame. It provides methods for analyzing motion using optical flow,
updating the ROI's position, drawing visual elements on video frames, and displaying
motion data on a scrolling axis plot.

Classes:
--------
ROI
    Represents a region of interest (ROI) for motion analysis, with methods
    for processing optical flow and visualizing results.

Imports:
--------
- QRect, QPoint (PySide6.QtCore): For representing and manipulating rectangular and point geometries.
- pg (pyqtgraph): For rendering scrolling axis plots.
- cv2 (OpenCV): For drawing rectangles, lines, and text on video frames.
- VideoAnalysisModule: For performing optical flow-based motion analysis.

Example Usage:
--------------
To use the module, instantiate the `ROI` class with a rectangular geometry and
arrow direction. Use the `analyze` method for motion detection and `draw_on_frame`
to visualize the ROI and its motion on video frames.
"""

from PySide6.QtCore import QRect, QPoint
import pyqtgraph as pg
import cv2
from .image_analysis import VideoAnalysis

class ROI:
    """Region of Interest (ROI) Class for Motion Analysis.

    The `ROI` class represents a rectangular area within a video frame for detecting
    and analyzing motion using optical flow. It integrates with the `VideoAnalysisModule`
    for performing optical flow calculations and provides methods for visualizing
    the ROI and its motion on video frames and scrolling axis plots.

    Attributes:
    ----------
    rect : QRect
        The rectangular area representing the region of interest.
    analysis_module : VideoAnalysisModule
        An instance of the `VideoAnalysisModule` for optical flow analysis within the ROI.
    cross_position : QPoint
        The current position of the cross intersection within the ROI, initialized to its center.

    Methods:
    -------
    __init__(rect: QRect, arrow_dir_x: float, arrow_dir_y: float) -> None
        Initializes the ROI with a rectangular geometry and arrow direction for motion analysis.
    update_cross_position(avg_flow_x: float, avg_flow_y: float) -> None
        Updates the position of the cross intersection based on the optical flow results.
    draw_on_frame(frame: cv2.Mat, roi_index: int) -> None
        Draws the ROI, cross intersection, and scrolling axis on the video frame.
    update_scrolling_axis(movement_buffers: dict, movement_curves: dict, max_frames: int, plot_widget: pg.PlotWidget) -> None
        Updates the scrolling axis data and renders it on the specified plot widget.
    """
    
    def __init__(self, 
                 rect: QRect, 
                 arrow_dir_x: float, 
                 arrow_dir_y: float) -> None:
        """
        Initialize the Region of Interest (ROI) with the given rectangle and arrow direction.

        Parameters
        ----------
        rect : QRect
            The rectangle representing the region of interest.
        arrow_dir_x : float
            The x component of the direction of the scrolling axis.
        arrow_dir_y : float
            The y component of the direction of the scrolling axis.
        """
        self.rect = rect
        self.analysis_module = VideoAnalysis(arrow_dir_x,
                                                   arrow_dir_y)
        self.cross_position = QPoint(rect.center().x(), rect.center().y())  # Initialize cross at ROI center

    def update_cross_position(self, 
                              avg_flow_x: float, 
                              avg_flow_y: float) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        Update the cross intersection position based on the optical flow results.
        The position wraps around when it goes out of the ROI.
        """      
        
        # Update cross position within the ROI bounds
        new_x = self.cross_position.x() + int(avg_flow_x)
        new_y = self.cross_position.y() + int(avg_flow_y)

        # Wrap around horizontally
        if new_x < self.rect.left():
            new_x = self.rect.right() - (self.rect.left() - new_x)
        elif new_x > self.rect.right():
            new_x = self.rect.left() + (new_x - self.rect.right())

        # Wrap around vertically
        if new_y < self.rect.top():
            new_y = self.rect.bottom() - (self.rect.top() - new_y)
        elif new_y > self.rect.bottom():
            new_y = self.rect.top() + (new_y - self.rect.bottom())

        self.cross_position.setX(new_x)
        self.cross_position.setY(new_y)

<<<<<<< HEAD
    def draw_on_frame(self, frame, roi_index):
=======
    def draw_on_frame(self, 
                      frame: cv2.Mat, 
                      roi_index: int) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        Draws the ROI rectangle, cross position, and scrolling axis on the given frame.
        """
        x, y, w, h = self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()

        # Draw ROI rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Draw X-axis and Y-axis through the ROI
        cross_x = self.cross_position.x()
        cross_y = self.cross_position.y()

        # X-axis: Horizontal line across the ROI
        cv2.line(frame, (x, cross_y), (x + w, cross_y), self.analysis_module.color, 2)

        # Y-axis: Vertical line across the ROI
        cv2.line(frame, (cross_x, y), (cross_x, y + h), self.analysis_module.color, 2)

        # Draw ROI label at the top-right corner
        label = f"ROI {roi_index + 1}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + w - text_size[0] - 5  # Right-align the text
        text_y = y + text_size[1] + 5  # Slightly below the top-right corner
        cv2.putText(
            frame,
            label,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,  # Font scale
            (0, 255, 0),  # Color (green)
            1,  # Thickness
            cv2.LINE_AA,
        )
    
<<<<<<< HEAD
    def update_scrolling_axis(self, movement_buffers, movement_curves, max_frames, plot_widget):
=======
    def update_scrolling_axis(self, 
                              movement_buffers: dict, 
                              movement_curves: dict, 
                              max_frames: int, 
                              plot_widget: pg.PlotWidget) -> None:
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
        """
        Updates the scrolling axis data and renders it on the plot widget.
        """
        if self not in movement_buffers:
            movement_buffers[self] = [0] * max_frames

        # Update movement buffer
        if len(movement_buffers[self]) >= max_frames:
            movement_buffers[self].pop(0)

        movement_buffers[self].append(self.analysis_module.current_velocity)

        # Update or create the curve
        if self not in movement_curves:
            curve_color = pg.mkColor(self.analysis_module.color)  # Use the ROI's assigned color
            movement_curves[self] = plot_widget.plot(
                pen=pg.mkPen(color=curve_color, width=2)
            )

        movement_curves[self].setData(movement_buffers[self])
        