import tkinter as tk
from numpy import arctan
from math import atan2
class crop_box(object):
    
    def __init__(self):
        self.roi_coordinates = None
        self.rectangle_drawed = None
        self.x1, self.y1 = 0
        self.x2, self.y2 = 0
        
    def start_roi_draw(self, event):
        self.roi_coordinates = []
        self.x1, self.y1 = event.x, event.y
        self.roi_coordinates.append([event.x, event.y])
        
    def draw_roi(self, event, canvas):
        canvas.delete('rectangle')
        self.rectangle_drawed = canvas.create_rectangle(self.x1, 
                                self.y1,
                                event.x, 
                                event.y, 
                                outline='red',
                                width=2,
                                tags='rectangle')

    def end_roi_draw(self, event, canvas, list):
        self.x2, self.y2 = event.x, event.y
        x_diff = abs(self.x2-self.x1)
        y_diff = abs(self.y2-self.y1)
        
        # If the box is too small, delete the box and
        # ask user to draw again
        if x_diff <= 10 or y_diff <= 10:
            self.x1 = 0
            self.y1 = 0
            self.x2 = 0
            self.y2 = 0
            return False
        
        canvas.delete('rectangle')
        self.rectangle_drawed = canvas.create_rectangle(self.x1, 
                        self.y1,
                        event.x, 
                        event.y, 
                        outline='red',
                        width=2,
                        tags='rectangle')
        self.roi_coordinates.append([self.x2, self.y2])
        list.append(self.roi_coordinates)
        
class arrow(object):
    def __init__(self):
        self.x1, self.y1 = 0
        self.x2, self.y2 = 0
        self.line_drawed = None
        
        self.virtual_overflow_direction = 0.0
        
        
    def start_arrow_draw(self, event):
        self.x1, self.y1 = event.x, event.y
        self.arrow_coordinates = []
        self.arrow_coordinates.append([event.x, event.y])
        
    def draw_arrow(self, event, canvas):
        canvas.delete('arrow')
        self.line_drawed = canvas.create_line(self.x1, 
                                                   self.y1,
                                                   event.x, 
                                                   event.y, 
                                                   width=2,
                                                   arrow=tk.LAST,
                                                   tags='arrow')

    def end_arrow_draw(self, event, canvas):
        self.x2, self.y2 = event.x, event.y
        self.arrow_coordinates.append([event.x, event.y])
        
        canvas.delete('arrow')
        self.line_drawed = canvas.create_line(self.x1, 
                                                   self.y1,
                                                   event.x, 
                                                   event.y, 
                                                   width=2,
                                                   arrow=tk.LAST,
                                                   tags='arrow')
        
        self.calculate_direction(self)
        return self.virtual_overflow_direction
    
    def calculate_direction(self):
        # temp = (self.y2 - self.y1) / (self.x2 - self.x1)
        # angle = arctan(temp)      
        
        angle = atan2((self.y2 - self.y1), (self.x2 - self.x1))
        print(angle)
        self.virtual_overflow_direction = -angle    # Negative sign because the pixel sequence
                                                    # in y-direction increases from the top
        

    
    