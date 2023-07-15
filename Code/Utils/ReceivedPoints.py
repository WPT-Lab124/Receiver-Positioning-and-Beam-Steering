#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
RecievedPoints class that manages the contours captured by the camera.

@ Author: Minshen Lin
@ Institute: Zhejiang University

@ LICENSE
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
'''

from itertools import combinations

# Type alias: here the name 'set' is actually tuple in python
_Point = (float, float)
_PointSet = (_Point, _Point, _Point, _Point, _Point)
_FourPointSet = (_Point, _Point, _Point, _Point)

class ReceivedPoints:
    """
    Managing received 5 points together with this class.
    """

    def __init__(self, point_set = None):
        """
        Constructor for the ReceivedPoints class.
        @point_set: The 5 received points stored as a tuple of (float, float).
        """
        self.point_set = point_set
    
    def update_points(self, new_point_set):
        """
        Update the stored point_set.
        """
        self.point_set = new_point_set
    
    def any_parallelogram(self):
        """
        Test whether any 4 of the total 5 points form a parallelogram: if there is,
        return the centroid of 4 points and the coordinates of the rest point as a
        tuple; otherwise, return None.
        """
        if self.point_set == None:
            return None

        if len(self.point_set) >= 4:
            four_points_combination = combinations(self.point_set, 4)

            for four_points in list(four_points_combination):
                if _isParallelogram(four_points):
                    centroid = _compute_centroid(four_points)
                    rest_point = self._compute_rest_point(four_points)
                    return (centroid, rest_point)
            return None

    def _compute_rest_point(self, four_points: _FourPointSet):
        """
        Returns the point that is not in the four_points set.
        """
        for point in self.point_set:
            if point not in four_points:
                return point
        return None
    
def _compute_mid_point(point1: _Point, point2: _Point) -> _Point:
    """
    Returns the mid point between two points.
    """
    return (point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2


def _compute_shortest_dist_squared(four_points: _FourPointSet):
    """
    Returns the shortest distance squared between two points from a point set.
    """
    two_points_combination = combinations(four_points, 2)

    dist_sq_list = []
    for two_points in list(two_points_combination):
        dist_sq_list.append(_compute_dist_squared(two_points[0], two_points[1]))

    return min(dist_sq_list)

def _compute_dist_squared(point1: _Point, point2: _Point):
    """
    Returns the distance squared between two points.
    """
    return (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2

def _parallelogram_test(mid_point_list: list, tolerance: float) -> bool:
    """
    Determination of a parallelogram via testing the overlapping between points in mid_point_list.
    """
    mid_point_combination = combinations(mid_point_list, 2)
    
    for two_points in list(mid_point_combination):
        if _overlap_test(two_points[0], two_points[1], tolerance):
            return True
    return False

def _overlap_test(mid_point1: _Point, mid_point2: _Point, tolerance: float) -> bool:
    """
    Whether 2 mid_points overlap in spatial coordinates.
    """
    dist_sq = (mid_point1[0] - mid_point2[0]) ** 2 + (mid_point1[1] - mid_point2[1]) ** 2

    if dist_sq <= tolerance:
        return True
    else:
        return False

def _compute_centroid(four_points: _FourPointSet):
    """
    Returns the centroid coordinates of the four points.
    """
    x, y = 0, 0
    for point in four_points:
        x += point[0]
        y += point[1]
    return (x / 4, y / 4)

def compute_parallelogram_sizes(four_points: _FourPointSet):
        size_squared = []
        two_points_combination = combinations(four_points, 2)
        for two_points in two_points_combination:
            size_squared.append(_compute_dist_squared(two_points[0], two_points[1]))
        return [x ** 0.5 for x in size_squared]

if __name__ == '__main__':
    # Run some test here
    point1 = (0.0, 1)
    point2 = (0.0, 1.1)
    point3 = (1, 0)
    point4 = (0, 0)
    point5 = (1, 1)
    point_set = (point1, point2, point3, point4, point5)

    rp = ReceivedPoints(point_set)
    print(rp.any_parallelogram())
