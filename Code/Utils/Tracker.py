#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracker class that keeps track of the laser spot and the receiver positions.

@ Author: Minshen Lin
@ Institute: Zhejiang University

@ LICENSE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from Utils.ReceivedPoints import ReceivedPoints
import time
import matplotlib.pyplot as plt

# Type alias: here the name 'set' is actually tuple in python
_Point = (float, float)
_PointSet = (_Point, _Point, _Point, _Point, _Point)

class Tracker:
    """
    A simple tracker class.
    """

    def __init__(self, received_points: ReceivedPoints, frame_threshold = 50):
        """
        The constructor for Tracker class.
        @received_points - The received points object.
        @frame_threshold - The number of consecutive frames a given object is allowed before labeling as disappeared
        """
        self.received_points = received_points
        self.frame_threshold = frame_threshold
        self.frame_count = 0
        
        self.init_time = time.time()
        self.time_list = []
        self.dist_squared_list = []
        
        if received_points.any_parallelogram() != None:
            self.receiver, self.laser_spot = received_points.any_parallelogram()
        else:
            self.receiver, self.laser_spot = None, None


    def positions(self):
        """
        Returns the coordinates of the receiver and the laser spot.
        """
        return self.receiver, self.laser_spot
    
    def _record_dist_squared(self):
        """
        Records the distance squared (for efficiency) between the receiver and the laser spot as a function of time.
        """
        if self.laser_spot != None:
            self.dist_squared_list.append(_compute_dist_squared(self.receiver, self.laser_spot))
            self.time_list.append(time.time())
            
    def plot_dist_func(self):
        """
        Plots the distance as a function of time.
        """
        time = [x - self.init_time for x in self.time_list]
        dist = [x ** 0.5 for x in self.dist_squared_list]
        plt.plot(time, dist)
        plt.show()
    
    def retrieve_stored_data_as_strings(self):
        """
        Retrives the stored time and dist arrays as two strings.
        """
        time = [x - self.init_time for x in self.time_list]
        dist = [x ** 0.5 for x in self.dist_squared_list]
        time_str = " ".join(str(x) for x in time)
        dist_str = " ".join(str(x) for x in dist)
        return time_str, dist_str
        
    def reset_storage(self):
        """
        Resets init_time, time_list, and dist_squared_list.
        """
        self.init_time = time.time()
        self.time_list = []
        self.dist_squared_list = []
            
def _compute_dist_squared(point1: _Point, point2: _Point):
    """
    Returns the distance squared between two points.
    """
    return (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2

if __name__ == '__main__':
    pass
