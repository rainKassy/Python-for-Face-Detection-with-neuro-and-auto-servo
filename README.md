# Python for Face Detection with Neuro and Auto Servo

## Description
This project implements a face tracking system using a camera and an Arduino. It employs two methods for face detection: DNN (Deep Neural Network) and Haar Cascade. The system can detect faces in real-time and adjust the camera's position based on the detected face's location.

## Files
1. **face_tracking_dnn.py**
   - This script uses a DNN model for face detection. It captures video frames, detects faces, and sends commands to the servos to track the largest detected face.
   - **Key Features**:
     - Uses OpenCV's DNN module for accurate face detection.
     - Smooth angle adjustment for servos to ensure stable tracking.
     - Returns the camera to a neutral position when no face is detected.

2. **face_tracking_haar.py**
   - This script uses Haar Cascade for face detection. Similar to the DNN approach, it captures video frames and adjusts the camera angle based on face position.
   - **Key Features**:
     - Utilizes Haar Cascade classifiers for faster face detection.
     - Simple implementation suitable for basic face tracking tasks.

3. **index.html**
   - This file contains the HTML interface for controlling the face tracking camera via a web browser.
   - **Key Features**:
     - Displays the video feed from the camera.
     - Provides buttons for manual control of the camera's movement.
     - Toggles between manual and automatic modes.

## Installation
1. Install the required packages:
   ```bash
   sudo apt install python3 python3-pip python3-opencv python3-picamera
pip install numpy pandas scikit-learn tensorflow keras torch opencv-python matplotlib seaborn
