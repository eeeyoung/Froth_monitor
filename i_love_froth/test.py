import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("Camera is working!")
    cap.release()
else:
    print("Failed to access the camera.")