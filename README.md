# Froth_monitor - A program for tracking the movement of froths of froth flotation in mineral processing

# Update: 21st Nov 2024
### Work in Progress

A dynamic and interactive application designed to analyze and visualize froth movement from video data using advanced image processing and data visualization techniques.

# Features
## 1. Arrow Direction Analysis:

Draw, lock, and display an arrow indicating the direction of froth overflow.
Customizable and adjustable arrow direction for flexible analysis.
## 2. Region of Interest (ROI) Detection:

Draw multiple ROIs on the video canvas.
Real-time movement analysis for each ROI.
Axis visualization (X and Y axes) within each ROI to track movement.
## 3. Video Processing:

Frame-by-frame video display with integrated image analysis.
Supports both local video files and live camera input.
## 4. Data Export:

Export analysis results as Excel files.
Customizable file naming and export directory.
Separate sheets for each ROI in the Excel output.
## 5. Replay and Reset:

Save and end the current session, clearing ROIs and resetting the interface for a new analysis.
## 6. Visualizations:

Real-time animation of velocity changes over frames.
Dedicated arrow canvas to display locked arrow direction.

__________________________________________________________________________________________________________________________________________________________________
# Update: 23rd Oct 2023
### Work in Progress

### To be realised (* means already done)
1. csv*
2. stop and restart new databook*
3. angle in degrees with manual typing (pre-set values choices)
4. programmed video with disappearing bubbles


# How to run the program from source code

1. Directly run the 'main_GUI.py' file in a suitable python environment

2. A UI should pop up with buttons. Click the 'Export' Menu to choose the file path you want the data to be stored, and edit the name you want to use.

3. Click the 'Import' menu option on the top left corner and choose to input a video by a local file or a real time webcam. If it is webcam, the video will be directly displaying on the canvas. If it is a local video, you need to click 'pause/play' button to start the video.

4. After input a video, by clicking 'add overflow direction', you should draw an arrow on the canvas indicating the direction of overflow of the froths. Or you can use the default value by directly going to step 4, the default value (-0.5pi) means direction goes vertically downwards.

5. Movement analysis is executed within each region of interest (ROI). You can draw one ROI on the video after click the 'Add ROI' button. You are not allowed to do so before inputting a video source.

6. A simple real-time data graph will display in cartesian coordinate system, which the y values shows the average velocities per second w.r.t. overflow direction.

7. After a video is finished, click the button 'export' to produce a excel databook, with each sheet refers to an ROI.
