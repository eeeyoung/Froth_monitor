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

    def draw_on_frame(self, frame, roi_index):
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
    
    def update_scrolling_axis(self, movement_buffers, movement_curves, max_frames, plot_widget):
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
        