#!/usr/bin/env python3

import os
import unittest

import context
import roboplot.config as config
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis as image_analysis


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class PathFollowingTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PathFollowingTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'PathFollowingTest')

    def testConvertFromSouth(self):
        config.x_pixels_to_points_scale = 1
        config.y_pixels_to_points_scale = 1
        points = [(0, 0), (3, 10), (5, 12), (7, 18), (9, 17)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.SOUTH
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (53, 50), (55, 52), (57, 58), (59, 57)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromNorth(self):
        config.x_pixels_to_points_scale = 1
        config.y_pixels_to_points_scale = 1
        points = [(0, 0), (3, 10), (5, 12), (7, 18), (9, 17)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.NORTH
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (47, 30), (45, 28), (43, 22), (41, 23)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromEast(self):
        config.x_pixels_to_points_scale = 1
        config.y_pixels_to_points_scale = 1
        points = [(0, 0), (3, 10), (5, 12), (7, 18), (9, 17)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.EAST
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (40, 43), (38, 45), (32, 47), (33, 49)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromWest(self):
        config.x_pixels_to_points_scale = 1
        config.y_pixels_to_points_scale = 1
        points = [(0, 0), (3, 10), (5, 12), (7, 18), (9, 17)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.WEST
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (60, 37), (62, 35), (68, 33), (67, 31)]
        self.assertEqual(output, expected_output_points)


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
