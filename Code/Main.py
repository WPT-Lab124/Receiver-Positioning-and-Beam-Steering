#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The program that implements receiver localization and beam steering.

@ Author: Minshen Lin
@ Institute: Zhejiang University

@ LICENSE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import cv2
import numpy as np
import subprocess as sp
import time
import datetime

# initialization stage
# initialize serial port with a default baudrate of 115200
import serial
serial_port = serial.Serial("/dev/serial0", 115200)

# initialize stepper motor controllers
from Utils.StepperMotor import Motor
motor_horizontal = Motor(serial_port, b'\x01')
motor_horizontal.set_angle_limits(-10, 10)
motor_vertical = Motor(serial_port, b'\x02')
motor_vertical.set_angle_limits(-10, 10)

# initialize PID controllers
from Utils.PID import PID
kp = -0.01; ki = -0.1; kd = 0
pid_vertical = PID(Kp = kp, Ki = ki, Kd = kd, setpoint = 0, sample_time = 0.033, output_limits = (-20, 20), differential_on_measurement = True)
pid_horizontal = PID(Kp = kp, Ki = ki, Kd = kd, setpoint = 0, sample_time = 0.033, output_limits = (-20, 20), differential_on_measurement = True)

# initialize a ReceivedPoints and a tracker to manage camera-captured contours
from Utils.ReceivedPoints import ReceivedPoints
from Utils.Tracker import Tracker
received_points = ReceivedPoints()
tracker = Tracker(received_points)

# global parameters
frame_count_limit = 1000 # modify this variable to change the operation time of the system
prevNumOfContours = 0
frame_count = 0
motor_enable = False

# operation stage
frames = []
frame_count = 0

# Video capture parameters
# (1280, 960) @ 40 fps
(width, height) = (1280, 960)
bytesPerFrame = width * height
fps = 40

# "raspividyuv" is the command that provides camera frames in YUV format
#  "--output -" specifies stdout as the output
#  "--timeout 0" specifies continuous video
#  "--luma" discards chroma channels, only luminance is sent through the pipeline
# see "raspividyuv --help" for more information on the parameters
videoCmd = "raspividyuv -w " + str(width) + " -h " + str(height) + " --output - --timeout 0 --framerate " + str(fps) + " --luma --nopreview"
videoCmd = videoCmd.split() # Popen requires that each parameter is a separate string

# initialize the parallel camera process
with sp.Popen(videoCmd, stdout = sp.PIPE) as cameraProcess:
    start_time = time.time()
    
    # wait for the first frame and discard it (only done to measure time more accurately)
    rawStream = cameraProcess.stdout.read(bytesPerFrame)
    
    print("Starting test protocol.")
    tracker.reset_storage()
    
    while frame_count < frame_count_limit:
        cameraProcess.stdout.flush() # discard any frames that we were not able to process in time
        
        frame = np.frombuffer(cameraProcess.stdout.read(bytesPerFrame), dtype=np.uint8) # Parse the raw stream into a numpy array
        
        if frame.size != bytesPerFrame:
            print("Error: Camera stream closed unexpectedly")
            break
        
        frame.shape = (height, width) # set the correct dimensions for the numpy array
        frame = cv2.inRange(frame, 50, 255) # create binary image
        contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frame_count += 1
        frames.append(frame) # store frames for future visualization
        
        # control logics
        if motor_enable == False:
            # if 5 contours are captured
            if len(contours) == 5:
                (center1, _) = cv2.minEnclosingCircle(contours[0])
                (center2, _) = cv2.minEnclosingCircle(contours[1])
                (center3, _) = cv2.minEnclosingCircle(contours[2])
                (center4, _) = cv2.minEnclosingCircle(contours[3])
                (center5, _) = cv2.minEnclosingCircle(contours[4])
                point_set = (center1, center2, center3, center4, center5)
                tracker.update(point_set) # update positions in the tracker
            
            if frame_count >= 100:
                motor_enable = True
                pid_horizontal.reset() # reset PID controllers, particularly the internal recorded time
                pid_vertical.reset()
            
            continue
       
        # if 5 contours are captured
        if len(contours) == 5:
            (center1, _) = cv2.minEnclosingCircle(contours[0])
            (center2, _) = cv2.minEnclosingCircle(contours[1])
            (center3, _) = cv2.minEnclosingCircle(contours[2])
            (center4, _) = cv2.minEnclosingCircle(contours[3])
            (center5, _) = cv2.minEnclosingCircle(contours[4])

            point_set = (center1, center2, center3, center4, center5)
            tracker.update(point_set) # update positions in the tracker
            (xSP, ySP), (xPV, yPV) = tracker.positions()
            
            # update PID setpoints and process variables
            pid_horizontal.setpoint = xSP
            xMV = pid_horizontal(xPV)
            time.sleep(0.005)
            motor_horizontal.move_to(xMV)
            
            pid_vertical.setpoint = ySP
            yMV = pid_vertical(yPV)
            time.sleep(0.005)
            motor_vertical.move_to(yMV)
            
            # record last-frame info
            prevNumOfContours = 5
            xSP_prev = xSP
            xPV_prev = xPV
            ySP_prev = ySP
            yPV_prev = yPV

        # if 4 contours are captured and 5 contours were captured in the last frame  
        if len(contours) == 4 and prevNumOfContours == 5:
            # perturb the stepper motors
            pid_horizontal.setpoint = xSP_prev
            xMV = pid_horizontal(xPV_prev)
            time.sleep(0.005)
            motor_horizontal.move_to(xMV)
            
            pid_vertical.setpoint = ySP_prev
            yMV = pid_vertical(yPV_prev)
            time.sleep(0.005)
            motor_vertical.move_to(yMV)
            
            prevNumOfContours = 4

    end_time = time.time()
    print("Done! Result: " + str(frame_count / (end_time - start_time)) + " fps")

# steer the motors to their zero positions
time.sleep(0.1)
motor_vertical.move_to_origin()
time.sleep(0.1)
motor_horizontal.move_to_origin()

serial_port.close() # close the open serial port

# display captured video
print("Display frames with OpenCV...")
for frame in frames:
    cv2.imshow("frame", frame)
    cv2.waitKey(1)
cv2.destroyAllWindows()
