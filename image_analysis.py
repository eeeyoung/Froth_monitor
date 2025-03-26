import cv2
import numpy as np
import openpyxl as op
from statistics import stdev
from copy       import copy
from math       import atan2

class image_analysis(object):
    def __init__(self, ResReduction, coordinates, overflow_direction, fps, number, color):
        
        self.ResReduction = ResReduction            # Factor of Reduction in Resolution  
        self.frame_rate = fps
        self.frame_count = 0
        self.std_threshold = 10
        self.search_template = None                 # Searched template
        self.search_space = None                    # Image where the search is running on
        self.excel_file_data = []                   # List storing data for later passing to excel workbook
        self.xy_graph_list = []
        self.biggest_vel = None

        self.number = number
        self.color = color
        
        self.third_x = None                         # Coordinates of search template
        self.third_y = None
        self.red_x = None
        self.red_y = None
        
        self.template_rectangle = None              # Store the coordinates of search template
        self.found_rectangle = None                 # Store the coordinates of matched template
        
        self.move_vector = None                     # Store the vector of movement per frame (delta_x, delta_y)
        self.move_vector_list = []
        
        self.velocity_list_std = []                 # Store the movement w.r.t. the overflow direction for 
                                                    # stdev calculation. The length is controlled 
        # self.list_len_std = 6
        self.list_len_std = fps*3
        
        self.velocity_list_avr = []                 # Store the movement w.r.t. the overflow direction for 
                                                    # average calculation. The lenght is controlled
        self.list_len_avg = None                    
        self.list_arg_count = 0
        self.average_velocity = None
        
        self.o_direct = -overflow_direction         # Store the value of overflow direction
        
        self.lt_cdn = coordinates[0]                # coordinates of the lefttop point of the ROI
        self.rb_cdn = coordinates[1]                # coordinates of the rightbottom point of the ROI
        self.axis_x = None                          # coordinates of the central of the axis which
        self.axis_y = None                          # displays the movement of the ROI
        
        self.shape_x = None
        self.shape_y = None

    def analyse_movement(self, image):

        if self.search_template is None:
            
            self.axis_x = (self.lt_cdn[0]+self.rb_cdn[0])//2
            self.axis_y = (self.lt_cdn[1]+self.rb_cdn[1])//2
            
            self.shape_x = image.shape[1]
            self.shape_y = image.shape[0]
            self.red_x = image.shape[1] // self.ResReduction
            self.red_y = image.shape[0] // self.ResReduction
            self.third_x = self.red_x // 3
            self.third_y = self.red_y // 3
            self.template_rectangle = (self.third_x, 
                                       self.third_y, 
                                       self.third_x,
                                       self.third_y)
            # whole_search_space = (0, 0, red_x, red_y)

            # Create a downsampled copy of the incoming image to reduce blurring
            temp_search_space = cv2.resize(image, (self.red_x, 
                                                   self.red_y))
            self.search_space = temp_search_space[0:self.red_y, 
                                                  0:self.red_x]
            
            found_rectangle = self.template_rectangle
            
            self.frame_count += 1
            self.frame_process_justification()

        else:
            # This is the normal movement analysis routine
            # Create a downsampled copy of the incoming image to reduce blurring
            temp_search_space = cv2.resize(image, (self.red_x, 
                                                   self.red_y))
            self.search_space = temp_search_space[0:self.red_y, 
                                                  0:self.red_x]
            
            # Convert images to grayscale
            grayscale_search_space = cv2.cvtColor(self.search_space, cv2.COLOR_BGR2GRAY)
            grayscale_template = cv2.cvtColor(self.search_template, cv2.COLOR_BGR2GRAY)
            
            # Run template matching
            result = cv2.matchTemplate(grayscale_search_space, grayscale_template, cv2.TM_CCOEFF_NORMED)
            cv2.imshow('', result)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            found_rectangle = (max_loc[0], max_loc[1], self.template_rectangle[2], self.template_rectangle[3])

            # Calculate the delta between the location of the best match to the search template and the initial position of the search template, scale up to original pixels
            self.move_vector = (found_rectangle[0] - self.template_rectangle[0]) * self.ResReduction, (found_rectangle[1] - self.template_rectangle[1]) * self.ResReduction
            
            # print('Move vector in progress: ', self.move_vector)
            
            self.frame_count += 1
            self.frame_process_justification()

        # Crop the current search space down to become the next pass' search template
        self.search_template = self.search_space[self.template_rectangle[1]:self.template_rectangle[1]+self.template_rectangle[3], 
                                                 self.template_rectangle[0]:self.template_rectangle[0]+self.template_rectangle[2]]

    def frame_process_justification(self):
        
        if_outlier = False
        vel_wrt_o = 0
        
        if self.frame_count > 1:
            vel_wrt_o = self.calculate_current_velocity()
            if_outlier = self.filter_and_record(vel_wrt_o)
            self.calculate_average_velocity(vel_wrt_o, if_outlier)
            self.xy_graph_list_append_and_fit()
            
        self.excel_data_append(vel_wrt_o, if_outlier)
        
    def display_movement(self, canvas):
        
        self.axis_x += self.move_vector[0]
        self.axis_y += self.move_vector[1]
        
        if self.axis_x >= self.rb_cdn[0]:
            self.axis_x -= self.shape_x
        elif self.axis_x <= self.lt_cdn[0]:
            self.axis_x += self.shape_x
        
    
        if self.axis_y >= self.rb_cdn[1]:
            self.axis_y -= self.shape_y
        elif self.axis_y <= self.lt_cdn[1]:
            self.axis_y += self.shape_y
            
            
        canvas.create_line(self.lt_cdn[0],
                           self.axis_y,
                           self.rb_cdn[0],
                           self.axis_y,
                           fill = 'black',
                           width = 4)
        
        canvas.create_line(self.axis_x,
                           self.lt_cdn[1],
                           self.axis_x,
                           self.rb_cdn[1],
                           fill = 'black',
                           width = 4)
        
        canvas_label = canvas.create_text(self.lt_cdn[0],
                                          self.lt_cdn[1],
                                          anchor='nw', 
                                          font=("Purisa", 30),
                                          fill=self.color)
        canvas.itemconfig(canvas_label,text = self.number)
        
        return

    def calculate_current_velocity(self):
    ### List to store each move vector
    ### Calculate average velocity over a certain number of frames/seconds
        print('Current frame count: ', self.frame_count)
        print('Current move vector: ', self.move_vector)
        
        vec_x = self.move_vector[0]
        vec_y = self.move_vector[1]
        
        x_2 = vec_x**2
        y_2 = vec_y**2
        vec_value = (x_2+y_2)**0.5
        
        if vec_x == 0 and vec_y == 0:
            return 0                                # Return urrent velocity which is zero
                                                    # No need to do below calculation
        
        else:
            if vec_x == 0:
                vec_angle = 0.5*np.pi               # Vertically upwards
            
            elif vec_y == 0:
                vec_angle = 0                       # Horizontally to the right
            
            else:
                vec_angle = atan2(vec_y, vec_x)  # Achieve the direction of current move vector

        angle_diff = vec_angle - self.o_direct
        vel_wrt_o = vec_value*np.cos(angle_diff)
        
        return vel_wrt_o

    def calculate_average_velocity(self, current_vel, if_outlier):
        if self.list_arg_count <= (self.frame_rate//2):
            if if_outlier == False:
                self.velocity_list_avr.append(current_vel)
            self.list_arg_count += 1
            
        else:
            if len(self.velocity_list_avr) == 0:
                self.average_velocity = 'All outliers for the past 0.5 second'
            else:
                self.average_velocity = sum(self.velocity_list_avr)/len(self.velocity_list_avr)
            self.velocity_list_avr = []
            self.list_arg_count = 0
               
    def filter_and_record(self, current_vel):
        # Store the current move_vector first
        self.move_vector_list.append(self.move_vector)

        if len(self.velocity_list_std) >= self.list_len_std:

            temp_velocity_list = self.velocity_list_std.copy()
            temp_velocity_list.pop(0)
            temp_velocity_list.append(current_vel)
            
            current_std = stdev(temp_velocity_list)
            
            if current_std >= self.std_threshold:
                print('current std is :', current_std)
                print('So current move vector does not take into account.')
                print('The velocity list is still: ', self.velocity_list_std)
                return True  # Means there is outlier
            else:
                self.velocity_list_std = temp_velocity_list
                # print('current std is :', current_std)
                # print('The new velocity list is: ', self.velocity_list_std)
                return False # No outlier

        else:
            self.velocity_list_std.append(current_vel)
            if len(self.velocity_list_std) == self.list_len_std:
                temp_std = stdev(self.velocity_list_std)*1.5
                if self.std_threshold < temp_std:
                    self.std_threshold  = temp_std
                print('The std for the first second is:', self.std_threshold)
            
            return False # No outlier
            
    def excel_data_append(self, current_vel, if_outlier):
        if if_outlier == True:
            OUTLIER = 'YES'
        else:
            OUTLIER = 'No'
            
        if self.frame_count == 1:
            self.excel_file_data.append(['FRAME COUNT', 
                                         'delta_X',
                                         'delta_Y',
                                         'CURRENT_vel',
                                         'OUTLIER?',
                                         'AVERAGE_vel_for_past_10_frames',
                                         ])
            
            self.excel_file_data.append([self.frame_count,
                                        'None',
                                        'None',
                                        'None',
                                        'None',
                                        self.average_velocity
                                        ])

        
        else:
            self.excel_file_data.append([self.frame_count,
                                        self.move_vector[0],
                                        self.move_vector[1],
                                        current_vel,
                                        OUTLIER,
                                        self.average_velocity
                                        ])

    def xy_graph_list_append_and_fit(self):
        if self.average_velocity is not None:
            self.xy_graph_list.append(self.average_velocity)

            if self.biggest_vel is None:
                self.biggest_vel = self.average_velocity

            else:
                if self.biggest_vel < abs(self.average_velocity):
                    self.biggest_vel = abs(self.average_velocity)

