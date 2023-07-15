#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StepperMotor class for the position control of stepper motors.

@ Author: Minshen Lin
@ Institute: Zhejiang University

@ LICENSE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import serial
import math
import time

def _degr2rad(angle):
    """
    Convert angle from degree to radian
    """
    return angle / 360 * 2 * math.pi

def _rad2deg(angle):
    """
    Convert angle from radian to degree
    """
    return angle / 2 / math.pi * 360

class Motor:
    '''
    The motor class keeps track of the state of a stepper motor and allows the
    user to steer the motor to the specified angle.
    '''
    
    micro_step = 16 #32 #16
    deg_per_step = 1.8 / micro_step
    
    
    def __init__(self, serial_port: serial.Serial, serial_address: bytes):
        """
        Constructor for the Motor class. 
        In this class, the current num of steps with respect to origin is recorded;
        if the angle is recorded instead, truncated and accumulated errors will
        be introduced.
        @serial_port - The serial port for communication.
        @serial_address - The serial address of this motor.
        """
        self.current_step = 0
        self.serial_port = serial_port
        self.serial_address = serial_address
        self.angle_limits = (0, 360)
   
    def angle_to_step(self, angle):
        """
        Converts angle (in degree) to the number of steps required to reach
        that angle.
        """
        current_angle = self.current_angle()
        angular_diff = angle - current_angle
        return int(angular_diff / Motor.deg_per_step)

    def current_angle(self):
        """
        Computes the current angle from recorded number of steps.
        """
        return self.current_step * Motor.deg_per_step
    
    
    def move_to(self, angle):
        """
        Steer the motor to the specified 'angle'. This function is written in a
        recursive manner to reduce redundancy.
        """
        # if angle exceeds angular limits, steer the motor to the limiting angles
        if self._is_angle_exceeding_upper_bound(angle):
            self.move_to(self.angle_limits[1])
            return
        elif self._is_angle_exceeding_lower_bound(angle):
            self.move_to(self.angle_limits[0])
            return
        
        # otherwise, steer the motor to the specified angle
        num_of_steps = self.angle_to_step(angle)
        if num_of_steps == 0:
            return
        # generate a serial command for steering
        command = bytearray(self.serial_address) # motor serial address （1 byte）
        # code 0xFD for moving command （1 byte）
        command.extend(b'\xfd')
        # direction， speed， and acceleration （3 bytes）
        if num_of_steps > 0:
            command.extend(b'\x14\xff\x00')
        else:
            command.extend(b'\x04\xff\x00')
        command.extend(abs(num_of_steps).to_bytes(3, byteorder = 'big')) # num of steps （3 bytes）
        command.extend(b'\x6b') # parity check （1 byte）
        
        self.serial_port.write(command) # write the command to motor via serial port
        self.current_step += num_of_steps # record the current num of steps
    
    def move_to_origin(self):
        """
        Steers the motor to origin (0 deg).
        """
        self.move_to(0)
        
    def set_current_pos_as_origin(self):
        """
        Sets the current position as the new origin point.
        """
        command = bytearray(self.serial_address)
        command.extend(b'\x0a\x6d\x6b')
        print('set command is')
        print(command)
        self.serial_port.write(command)
        self.current_step = 0
        
    def set_origin_to_angle(self, angle):
        """
        """
        self.move_to(angle)
        time.sleep(0.01)
        self.set_current_pos_as_origin()
    
    def set_angle_limits(self, lower_bound: float, upper_bound: float):
        """
        Set angle limits that the motor can move within.
        """
        self.angle_limits = (lower_bound, upper_bound)
        
    def _is_angle_exceeding_upper_bound(self, angle):
        """
        Whether the angle exceeds the upper angle limit.
        """
        if angle > self.angle_limits[1]:
            return True
        return False
    
    def _is_angle_exceeding_lower_bound(self, angle):
        """
        Whether the angle exceeds the lower angle limit.
        """
        if angle < self.angle_limits[0]:
            return True
        return False
     

if __name__ == '__main__':
    # Testing the functionalities of this class
    
    # initialize seiral with a default baudrate of 115200
    serial_port = serial.Serial("/dev/serial0", 115200)
    motor1 = Motor(serial_port, b'\x01')
    motor1.set_angle_limits(-22.5, 22.5)
    
    # motor1.set_origin_to_angle(-2.5) # negative number moves right
    
    time.sleep(0.1)
    
    motor2 = Motor(serial_port, b'\x02')
    motor2.set_angle_limits(-22.5, 22.5)
    

    motor2.set_origin_to_angle(-2.5) # negative number moves downwards
        
    serial_port.close()