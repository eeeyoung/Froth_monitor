import tkinter as tk
import cv2
import numpy as np
import openpyxl as op

from ROI_and_arrow_drawing  import crop_box, arrow
from image_analysis         import image_analysis
from tkinter                import filedialog
from PIL                    import ImageTk, Image
from pygrabber.dshow_graph  import FilterGraph
from datetime               import datetime

class xy_canvas:
    def __init__(self, master):
        self.height = 150
        self.starting_point = self.height // 2
        self.width = 700
        self.number_of_lines = 0
        
        self.biggest_value_list = []

        self.xy_graph_dict = {}
        self.vel_list_dict = {}
        self.temp = None
        
        self.xy_canvas = tk.Canvas(master, height=self.height, width=self.width)
        self.xy_canvas.grid(row=8, column=2, rowspan=3, columnspan=6)
        
        self.xy_canvas_label = self.xy_canvas.create_text(10, 10, anchor='nw', font=30)
        self.xy_canvas.itemconfig(self.xy_canvas_label,
                                  text = '+')

        self.xy_canvas_label = self.xy_canvas.create_text(10, 130, anchor='nw', font=30)
        self.xy_canvas.itemconfig(self.xy_canvas_label,
                                  text = '-')
  
    def update_xy_graph(self, vel_list, biggest_vel, ROI_number):
        if ROI_number > self.number_of_lines:
            if len(vel_list) >= 3:
                self.number_of_lines += 1
        
        if len(vel_list)%2 != 0:
            return

        
        if ROI_number <= self.number_of_lines:
            self.store_biggest_vel(biggest_vel)
            self.store_vel_list(vel_list, ROI_number)

            if ROI_number == self.number_of_lines:
                
                self.xy_canvas.delete('lines')
                temp = self.get_biggest_vel()

                for i in range (1, ROI_number+1):
                    ROI_name = f'ROI_%i'%i
                    vel_list = self.fit_lines(temp, self.vel_list_dict[ROI_name])
                    
                    # Colour allocation for different ROI's lines
                    if i == 1:
                        color = 'red'
                    elif i == 2:
                        color = 'black'
                    elif i == 3:
                        color = 'blue'
                    elif i == 4:
                        color = 'green'
                    elif i == 5:
                        color = 'yellow'
                    

                    for k in range (1, len(vel_list)-2, 2):
                        self.xy_canvas.create_line(self.width-k,
                                                vel_list[-k]+self.starting_point,
                                                self.width-k-2,
                                                vel_list[-k-2]+self.starting_point,
                                                width=4,
                                                fill=color,
                                                tags='lines')
                
                        # self.xy_canvas.create_line(self.width-k-1,
                        #                            vel_list[-k-1]+self.starting_point,
                        #                            self.width-k-2,
                        #                            vel_list[-k-2]+self.starting_point,
                        #                            width=4,
                        #                            fill=color,
                        #                            tags='lines')
                        
                        if k == self.width:
                            break
                        
                self.biggest_value_list = []
    
    def store_biggest_vel(self, biggest_vel):
        self.biggest_value_list.append(biggest_vel)
        return
    
    def store_vel_list(self, vel_list, ROI_number):
        ROI_name = f'ROI_%i'%ROI_number
        self.vel_list_dict[ROI_name] = vel_list
        return
        
    def get_biggest_vel(self):
        biggest_vel = max(self.biggest_value_list)
        temp = (self.height//2) // biggest_vel
        self.biggest_value_list = []
        return temp

    def fit_lines(self, temp, vel_list):
        temp_list = []
        for vel in vel_list:
            vel = int(temp*vel)
            temp_list.append(vel)
        return temp_list


    
class main_GUI:
    def __init__(self):
        # Basic video/camera properties
        self.ret = None                                 # If any frame is being read
        self.frame = None                               # The frame is currently reading
        self.video_capture = None                       # Store the videocapture variable of cv2
        self.canvas_image = None                        # Image to be displayed on main canvas
        self.if_video_playing = False                   # If the video is playing
        self.if_video_imported = False                  # If video is imported
        self.if_camera_imported = False                 # If camera is loaded
        self.video_fps = 30                             # Fps of the video, default as 30                 
        self.frame_interval = 0                         # Time interval between each frame

        # ROI setting
        self.if_ROI = False                             # If any ROI exists
        self.if_cropping_box = False                    # If cropping ROI is ongoing
        self.ROI_drawing = None                         # Create to store the new instance of cropping box
        self.ROI_coordinates_list = []                  # Store the coordinates of every ROI
        self.number_of_ROIs = 0                         # Number of ROIs
        self.ROIs_dict = {}                             # Dictionary that pair of ROIs and their instance
                                                        # of image analysis
        self.ResReduction = 2
            
        # Initialize a excel databook
        self.data_book = op.Workbook()                  # Create a excel workbook for storing data 
        
        # Overflow direction setting
        self.arrow = None                               # Create to store the instance of the arrow
                                                        # that indicates overflow direction
        self.if_arrow = False                           # If any direction of flow exists
        self.arrow_drawing = False                      # If the arrow drawing is in progress
        self.use_default_direction = False              # If use the default overflow direction
        self.virtual_overflow_direction = -0.5*np.pi    # Overflow direction in value                                 
        
        
        # Define the UI
        self.root = tk.Tk()
        self.root.title('I love Froths')
        self.popup = None

        # Define the Menubar    
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        # First Menu - Import
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label='import local video', command=self.import_local_video)
        self.file_menu.add_command(label='load camera', command=self.camera_menu_initialize)
        self.selected_camera = tk.StringVar()
        self.available_cameras = {}
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit')
        self.menu_bar.add_cascade(label='Import', menu=self.file_menu)
        # Second Menu - Export
        self.export_routine = './'                      # The location of ROI data to be stored
        self.datetime = str(datetime.now())
        self.export_name = tk.StringVar()
        self.export_name.set(f'%s.xlsx'%self.datetime[:-16])
        self.if_exported = False
        
        self.export_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.export_menu.add_command(label='Export settings', command=self.export_setting_window)
        self.menu_bar.add_cascade(label='Export', menu=self.export_menu)
        
        # Define buttons
        for i in range(0, 10):
            for k in range(0, 8):
                self.button = tk.Button(self.root, text='')
                self.button.config(height=2, width=15)
                self.button.grid(row=i, column=k, padx=2, pady=2)
        
        self.button = tk.Button(self.root, text='Add overflow direction', command=self.add_arrow_initialize)
        self.button.config(height=2, width=32)
        self.button.grid(row=0, column=0, padx = 2, pady= 2, columnspan=2)

        self.button = tk.Button(self.root, text='Add one ROI', command=self.crop_box_initialize)
        self.button.config(height=2, width=32)
        self.button.grid(row=1, column=0, padx = 2, pady= 2, columnspan=2)
        
        self.if_video_paused = True
        self.button = tk.Button(self.root, text='Pause/Play', command=self.pause_play)
        self.button.config(height=2, width=32)
        self.button.grid(row=2, column=0, padx = 2, pady= 2, columnspan=2)

        self.button = tk.Button(self.root, text='Save and Quit', command=self.excel_file_output)
        self.button.config(height=2, width=32)
        self.button.grid(row=4, column=0, padx = 2, pady= 2, columnspan=2)
        
        # Defin the canvas
        self.video_canvas_height = 400
        self.video_canvas_width = 700
        self.video_canvas = tk.Canvas(self.root, 
                                      height=self.video_canvas_height, 
                                      width=self.video_canvas_width,
                                      bg='green')
        self.video_canvas.grid(row=0, column=2, rowspan=8, columnspan=6)
        self.scaling_factor_width = None
        self.scaling_factor_width = None
        self.scaling_factor_final = None
        self.video_canvas.bind('<ButtonPress-1>', self.mouse_event_justification)
        self.video_canvas.bind('<B1-Motion>', self.mouse_event_justification)
        self.video_canvas.bind('<ButtonRelease-1>', self.mouse_event_justification)
        
        # canvas for relative movements in real time
        self.xy_canvas = xy_canvas(self.root)
        
        # Define the labels indicating the overflow direction
        self.label = tk.Label(self.root, text='Overflow\ndirection:')
        self.label.config(height=2, width=15)
        self.label.grid(row=3, column=0)

        self.label = tk.Label(self.root, text=f'%f rad'%self.virtual_overflow_direction, bg='red')
        self.label.config(height=2, width=15)
        self.label.grid(row=3, column=1)
        
        self.save_and_quit = False
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
      
        if self.if_exported==False and self.number_of_ROIs>0:
            self.warning(trigger='Didnt save')
        
        else:
            self.root.destroy()
        
    def warning(self, trigger):
        self.popup = tk.Toplevel(self.root)
        self.popup.title('Warning')
        
        if trigger == 'No video':
            text = 'Please input a video or load a webcam first!'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            close_button = tk.Button(self.popup, text='OK', command=self.popup.destroy)
            close_button.pack()
            
        elif trigger == 'No arrow':
            text = 'You have not draw overflow direction yet. \nDraw one or use the default value?'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            draw_button = tk.Button(self.popup, text='Draw one', command=self.add_arrow_initialize)
            draw_button.pack()
            default_button = tk.Button(self.popup, text='Use default value', command=self.set_arrow_default)
            default_button.pack()
        
        elif trigger == 'Arrow drawing':
            text = 'Please finish the current arrow drawing first!'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            close_button = tk.Button(self.popup, text='OK', command=self.popup.destroy)
            close_button.pack()
        
        elif trigger == 'Video error':
            text = 'Error: Could not open the video file!'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            close_button = tk.Button(self.popup, text='OK', command=self.popup.destroy)
            close_button.pack()
        
        elif trigger == 'Overlap action':
            text = 'Please finish the ongoing action first!'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            close_button = tk.Button(self.popup, text='OK', command=self.popup.destroy)
            close_button.pack()

        elif trigger == 'No pause under camera play':
            text = 'Pause function is disabled under camera playing!'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            close_button = tk.Button(self.popup, text='OK', command=self.popup.destroy)
            close_button.pack()       
            
        elif trigger == 'Didnt save':
            text = 'You have not export the data, do you want to export them?'
            text_label = tk.Label(self.popup, text=text)
            text_label.pack()
            save_button = tk.Button(self.popup,
                                    text='Save and Quit',
                                    command=self.excel_file_output)
            save_button.pack()
            close_button = tk.Button(self.popup, 
                                     text='Directly Quit', 
                                     command=self.root.destroy)
            close_button.pack()               
            
    def label_notification(self, trigger):
        if trigger == 'arrow drawing':
            self.ROI_drawing_label = tk.Label(self.root, text='Overflow Direction\nDrawing', 
                                              font=('Times New Roman','11'), 
                                              fg='red')
            self.ROI_drawing_label.grid(row = 7, column=4, sticky='n')
            
        if trigger == 'ROI drawing':
            self.ROI_drawing_label = tk.Label(self.root, text='ROI  Drawing', 
                                              font=('Times New Roman','12'), 
                                              fg='red')
            self.ROI_drawing_label.grid(row = 7, column=4, sticky='n')
    
    def export_setting_window(self):

        def export_settings():
            # Create a pop-up dialog to choose a file path
            self.export_routine = filedialog.askdirectory(
                title="Choose a directory to export data"
            )

            # Check if a file path was selected
            if self.export_routine:
                print("Selected file path:", self.export_routine)
                
        export_window = tk.Toplevel(self.root)
        export_window.title('Select Export Directory')
        export_window.attributes('-topmost', True)

        export_label = tk.Label(export_window,
                                text='File path: ')
        export_label.config(height=2,
                            width=15)
        export_label.grid(row=0, column=0)
        
        export_button = tk.Button(export_window, 
                                  text="Browse", 
                                  command=export_settings)
        export_button.grid(row=0, column=1)

        
        export_label = tk.Label(export_window,
                                text='File name: ')
        export_label.config(height=2,
                            width=15)
        export_label.grid(row=1, column=0)
    
        file_name_entry = tk.Entry(export_window, 
                                   textvariable=self.export_name, 
                                   width=30)
        file_name_entry.grid(row=1, column=1)
        
        export_button = tk.Button(export_window,
                                  text='OK',
                                  command=export_window.destroy)
        export_button.grid(row=2, column=2)            
    
    # Import local video and display the first frame
    def import_local_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
    
        if file_path:
            self.video_capture = cv2.VideoCapture(file_path)
            
            if not self.video_capture.isOpened():
                self.warning(trigger = 'Video error')
                return
            
            self.ret, self.frame = self.video_capture.read()
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            
            self.get_fps()
            self.get_scaling_factor()
            
            # Scale the graph to fit inside the canvas
            self.frame = cv2.resize(self.frame, None, fx=self.scaling_factor_final, fy=self.scaling_factor_final)
            
            self.canvas_image = Image.fromarray(self.frame)
            self.canvas_image = ImageTk.PhotoImage(image=self.canvas_image)
            self.video_canvas.create_image(0,0,anchor = tk.NW,image=self.canvas_image)
            self.if_video_imported = True

            
            self.frame_interval = int(1000 // self.video_fps)
            print('fps: ', self.video_fps)

    def load_camera(self, camera_index):
        self.video_capture = cv2.VideoCapture(int(camera_index))
        
        # Disable the pause/play function
        self.if_video_paused = False
        self.if_camera_imported = True
        self.if_video_imported = True
        self.selection_window.destroy
        
        self.get_fps()
        self.get_scaling_factor()
        self.frame_interval = int(1000 // self.video_fps)
            
        self.play_video()
        
    def camera_menu_initialize(self):
        
        def option_menu_callback(selection):

            # If user choose any option, pass the option to 
            # camera loading function
            for key, value in self.available_cameras.items():
                self.load_camera(key[7])
        
        # Create a window for camera selection
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title('Select Camera')
        
        self.camera_label = tk.Label(self.selection_window, 
                                     text='Select Camera: ')
        self.camera_label.config(height=2, width=15)
        self.camera_label.pack(side='left')
        
        self.available_cameras = self.get_camera_option()
            
        print('available cameras: ', self.available_cameras)
        
        self.camera_dropdown = tk.OptionMenu(self.selection_window,
                                             self.selected_camera,
                                             self.available_cameras,
                                             command=option_menu_callback)
        self.camera_dropdown.pack(side='left')
        
        self.ok_button = tk.Button(self.selection_window,
                                   text = 'OK',
                                   command=self.selection_window.destroy)
        self.ok_button.pack(side='left')
        
    def get_camera_option(self):
        
        devices = FilterGraph().get_input_devices()
        
        available_cameras = {}
        
        for device_index, device_name in enumerate(devices):
            device_key = f'Camera %i: '%device_index
            available_cameras[device_key] = device_name
            
        return available_cameras
           
    def get_fps(self):
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
    
    def get_scaling_factor(self):
        self.scaling_factor_width = self.video_canvas_width / self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.scaling_factor_height = self.video_canvas_height / self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.scaling_factor_final = min(self.scaling_factor_height,
                                        self.scaling_factor_width)
        print('Width scaling factor: ', self.scaling_factor_width)
        print('Height scaling factor: ', self.scaling_factor_height)

    # Pause or play the video
    def pause_play(self):
        if self.if_camera_imported:
            self.warning(trigger='No pause under camera play')
            return
        
        if self.if_video_imported is False:
            self.warning(trigger = 'No video')
        
        else:
            self.if_video_paused = not self.if_video_paused
            if self.if_video_playing == False:
                self.play_video()
                self.if_video_playing = True
    # Main function of video playing
    def play_video(self): 
        
        # if not paused
        if self.if_video_paused is False:
            if self.video_capture is not None:
                self.video_canvas.delete('all')
                self.ret, self.frame = self.video_capture.read()          # Read the video
    
                # if not self.ret:
                #     self.excel_file_output()
                #     return
                
                self.frame = cv2.resize(self.frame, None, fx=self.scaling_factor_final, fy=self.scaling_factor_final)
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

                # Essential code to display images on tkinter's canvas
                self.canvas_image = Image.fromarray(self.frame)
                self.canvas_image = ImageTk.PhotoImage(image=self.canvas_image)
                self.video_canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
                
                # Display the ROIs
                if self.if_ROI:
                    for i in range(0, self.number_of_ROIs):
                        c1 = self.ROI_coordinates_list[i][0]
                        c2 = self.ROI_coordinates_list[i][1]
                        self.video_canvas.create_rectangle(c1, c2, width=2, outline='red') 
                    self.image_analysis_displaying()
                
                # Display the overflow direction arrow
                if self.if_arrow:
                    self.arrow_displaying()
            
                self.video_canvas.after(self.frame_interval, self.play_video)
    
        else:
            self.video_canvas.after(self.frame_interval, self.play_video)          

    def crop_box_initialize(self):
        if self.if_video_imported is False:
            self.warning(trigger = 'No video')
        
        else:
            if self.if_cropping_box == True:
                self.warning(trigger = 'Overlap action')
                return
                
            # If an overflow direction arrow has not been drawed and
            # user did not choose to use the default direction value
            # popup a window asking user to choose
            if not self.if_arrow:
                if self.arrow_drawing is True:
                    self.warning(trigger='Arrow drawing')
                    return
                if not self.use_default_direction:
                    self.warning(trigger='No arrow')
                    return
            
            self.if_cropping_box = True
            self.ROI_drawing = crop_box     # create a new instance for the ROI
            
            self.label_notification(trigger='ROI drawing')
            
    def crop_box_ongoing(self, event):

        # if the event is triggered by clicking
        if event.type == '4':
            self.ROI_drawing.start_roi_draw(self.ROI_drawing, 
                                            event)
        # if the event is trggered by dragging
        if event.type == '6':
            self.ROI_drawing.draw_roi(self.ROI_drawing, 
                                      event,
                                      self.video_canvas)
        # if the event is trggered by releasing
        if event.type == '5':
            drawed = self.ROI_drawing.end_roi_draw(self.ROI_drawing, 
                                                   event,
                                                   self.video_canvas,
                                                   self.ROI_coordinates_list)

            if drawed == False: # if the drawed box is too small
                
                popup = tk.Toplevel(self.root)
                popup.title('Warning')
                text_label = tk.Label(popup, text='Too small ROI, please draw again!')
                text_label.pack()
                close_button = tk.Button(popup, text='Redraw', command=popup.destroy)
                close_button.pack()
                
                self.video_canvas.delete('rectangle')
        
            else:
                self.number_of_ROIs = len(self.ROI_coordinates_list)
                print('Number of ROIs: ', len(self.ROI_coordinates_list))
                print('Coordinates of them: ', self.ROI_coordinates_list)
                
                self.ROI_drawing = None
                self.if_cropping_box = False
                self.if_ROI = True
                
                self.ROI_drawing_label.destroy()
                self.image_analysis_initialize()
                
    def image_analysis_initialize(self):
        i = self.number_of_ROIs
        ROI_name = f'ROI_%i'%i
        
        if i == 1:
            color = 'red'
        elif i == 2:
            color = 'black'
        elif i == 3:
            color = 'blue'
        elif i == 4:
            color = 'green'
        elif i == 5:
            color = 'yellow'

        self.ROIs_dict[ROI_name] = image_analysis(self.ResReduction, 
                                                  self.ROI_coordinates_list[i-1], 
                                                  self.virtual_overflow_direction,
                                                  self.video_fps,
                                                  i,
                                                  color)

        # x and y are FLIPPED when cropping, so img[y:y+h, x:x+w]
        self.ROIs_dict[ROI_name].analyse_movement(self.frame[self.ROI_coordinates_list[i-1][0][1]:self.ROI_coordinates_list[i-1][1][1],
                                                             self.ROI_coordinates_list[i-1][0][0]:self.ROI_coordinates_list[i-1][1][0]])
           
    def image_analysis_displaying(self):
        for i in range (1, self.number_of_ROIs+1):

            ROI_name = f'ROI_%i'%i
            self.ROIs_dict[ROI_name].analyse_movement(self.frame[self.ROI_coordinates_list[i-1][0][1]:self.ROI_coordinates_list[i-1][1][1],
                                                                self.ROI_coordinates_list[i-1][0][0]:self.ROI_coordinates_list[i-1][1][0]])
            self.ROIs_dict[ROI_name].display_movement(self.video_canvas)
            
            self.xy_canvas.update_xy_graph(self.ROIs_dict[ROI_name].xy_graph_list,
                                           self.ROIs_dict[ROI_name].biggest_vel,
                                           i)
    
    def add_arrow_initialize(self):
        if self.if_arrow is True:
            return
        
        if self.if_video_imported is False:
            self.warning(trigger = 'No video')
            return

        if self.use_default_direction == False:
            self.arrow_drawing = True
            self.arrow = arrow
            print('initialized')
            self.label_notification(trigger='arrow drawing')
        
        if self.popup is not None:
            self.popup.destroy()
        return
        
    def set_arrow_default(self):
        self.use_default_direction = True
        if self.popup:
            self.popup.destroy()
        print('The overflow direction is set as:', self.virtual_overflow_direction)
        self.crop_box_initialize()
    
    def add_arrow_drawing(self, event):
        
        # if the event is triggered by clicking
        if event.type == '4':
            self.arrow.start_arrow_draw(self.arrow,
                                        event)
        # if the event is trggered by dragging
        if event.type == '6':
            self.arrow.draw_arrow(self.arrow,
                                  event,
                                  self.video_canvas)
    
        # if the event is trggered by releasing
        if event.type == '5':
            self.virtual_overflow_direction = self.arrow.end_arrow_draw(self.arrow,
                                                                event,
                                                                self.video_canvas)
            self.arrow_drawing = False
            self.if_arrow = True
            self.ROI_drawing_label.destroy()
            self.root.update_idletasks()
            self.label = tk.Label(self.root, text=f'%f rad'%self.virtual_overflow_direction, bg='red')
            self.label.config(height=2, width=15)
            self.label.grid(row=3, column=1)
            print('overflow_direction is: ', self.virtual_overflow_direction)

        return

    def arrow_displaying(self):
        self.line_drawed = self.video_canvas.create_line(self.arrow.x1, 
                                                         self.arrow.y1,
                                                         self.arrow.x2, 
                                                         self.arrow.y2, 
                                                         width=2,
                                                         arrow=tk.LAST,
                                                         tags='arrow')
        
    def mouse_event_justification(self, event):
        
        if self.arrow_drawing:
            self.add_arrow_drawing(event)
            return
        
        if self.if_cropping_box:
            self.crop_box_ongoing(event)
            
    def excel_file_output(self):
        if self.if_exported == True:
            return
        
        self.export_name = self.export_routine + str('/%s'%self.export_name.get())
        for i in range (1, self.number_of_ROIs+1):
            ROI_name = f'ROI_%i'%i
            if i == 1:
                data_sheet = self.data_book.active
                data_sheet.title = ROI_name
            else:
                data_sheet = self.data_book.create_sheet(title=ROI_name)
            for row in self.ROIs_dict[ROI_name].excel_file_data:
                data_sheet.append(row)
                        
        self.data_book.save(self.export_name+'.xlsx')
        self.if_exported = True
        
        self.root.destroy()

        
main_GUI()