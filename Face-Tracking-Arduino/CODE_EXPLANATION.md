# Explanation of Code Syntax

This document provides explanations for the main components of the face tracking Arduino code.

## Imports
- `import cv2`: Imports OpenCV for image processing.
- `import numpy as np`: Imports NumPy for numerical operations.
- `import serial`: Imports PySerial for serial communication with Arduino.
- `from picamera2 import Picamera2`: Imports the Picamera2 library for camera management.
- `import time`: Imports the time library for time-related functions.

## Constants
- `SERIAL_PORT`: Defines the serial port for Arduino.
- `BAUD_RATE`: Sets the baud rate for serial communication.
- `SENSITIVITY`: Defines how sensitive the servo movements are to face position changes.
- `face_cascade_path`: Path to the Haar cascade classifier for face detection.

## Main Functions
### send_command(angle_x, angle_y)
Sends commands to the servo motors via serial communication.

### main loop
Captures frames from the camera, detects faces, and adjusts the camera position accordingly.
