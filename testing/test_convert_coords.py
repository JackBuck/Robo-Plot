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
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.SOUTH
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (53, 50), (55, 52), (57, 58), (59, 57)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromNorth(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.NORTH
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (47, 30), (45, 28), (43, 22), (41, 23)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromEast(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.EAST
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (40, 43), (38, 45), (32, 47), (33, 49)]
        self.assertEqual(output, expected_output_points)

    def testConvertFromWest(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.WEST
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (60, 37), (62, 35), (68, 33), (67, 31)]
        self.assertEqual(output, expected_output_points)

    def testConvertWithDefaultParam(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 0.2
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 0.2
        config.CAMERA_RESOLUTION = (200, 200)
        points = [(0, 100), (13, 120), (85, 122), (27, 128), (150, 130)]
        centre = (50, 40)

        scan_direction = image_analysis.Direction.SOUTH
        output = path_following.convert_to_global_coords(points, scan_direction, centre)
        expected_output_points = [(50, 40), (52.6, 44), (67, 44.4), (55.4, 45.6), (80, 46)]
        self.assertEqual(output, expected_output_points)


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
