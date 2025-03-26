## Work in Progress
## Last update: 2nd Oct 2023


## Check the 'package_requirements.txt' to see the requirements for running this source code. If missing, you can directly use pip install command in the terminal to install, the name of the package is the same as it shows in this text file.

#
1. csv
2. stop and restart new databook
3. angle in degrees with manual typing (pre-set values choices)
4. programmed video with disappearing bubbles


## How to run the program from source code

1. Directly run the 'main_GUI.py' file in a suitable python environment


2. A UI should pop up with buttons. Click the 'Export' Menu to choose the file path you want the data to be stored, and edit the name you want to use.


3. Click the 'Import' menu option on the top left corner and choose to input a video by a local file or a real time webcam. If it is webcam, the video will be directly displaying on the canvas. If it is a local video, you need to click 'pause/play' button to start the video.


4. After input a video, by clicking 'add overflow direction', you should draw an arrow on the canvas indicating the direction of overflow of the froths. Or you can use the default value by directly going to step 4, the default value (-0.5pi) means direction goes vertically downwards.


5. Movement analysis is executed within each region of interest (ROI). You can draw one ROI on the video after click the 'Add ROI' button. You are not allowed to do so before inputting a video source.


6. A simple real-time data graph will display in cartesian coordinate system, which the y values shows the average velocities per second w.r.t. overflow direction.


7. After a video is finished, click the button 'export' to produce a excel databook, with each sheet refers to an ROI.