#!/usr/bin/env python3

import os
import unittest

import context
import roboplot.config as config
import roboplot.core.camera.camera_utils
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis_enums as image_analysis_enums


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class ConvertCoordsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ConvertCoordsTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'ConvertCoordsTest')

    def testConvertFromSouth(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis_enums.Direction.SOUTH
        output = roboplot.core.camera.camera_utils.convert_to_global_coords(points,
                                                                            scan_direction,
                                                                            centre,
                                                                            0,
                                                                            config.CAMERA_RESOLUTION[0] //2)

        expected_output_points = [[50, 40], [53, 50], [55, 52], [57, 58], [59, 57]]
        self.assertEqual(output, expected_output_points)

    def testConvertFromNorth(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis_enums.Direction.NORTH
        output = roboplot.core.camera.camera_utils.convert_to_global_coords(points,
                                                                            scan_direction,
                                                                            centre,
                                                                            0,
                                                                            config.CAMERA_RESOLUTION[0] //2)
        expected_output_points = [[50, 40], [47, 30], [45, 28], [43, 22], [41, 23]]
        self.assertEqual(output, expected_output_points)

    def testConvertFromEast(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis_enums.Direction.EAST
        output = roboplot.core.camera.camera_utils.convert_to_global_coords(points,
                                                                            scan_direction,
                                                                            centre,
                                                                            0,
                                                                            config.CAMERA_RESOLUTION[0]/2)

        expected_output_points = [[50, 40], [40, 43], [38, 45], [32, 47], [33, 49]]
        self.assertEqual(output, expected_output_points)

    def testConvertFromWest(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 1
        config.CAMERA_RESOLUTION = (20, 20)
        points = [(0, 10), (3, 20), (5, 22), (7, 28), (9, 27)]
        centre = (50, 40)

        scan_direction = image_analysis_enums.Direction.WEST
        output = roboplot.core.camera.camera_utils.convert_to_global_coords(points,
                                                                            scan_direction,
                                                                            centre,
                                                                            0,
                                                                            config.CAMERA_RESOLUTION[0] //2)

        expected_output_points = [[50, 40], [60, 37], [62, 35], [68, 33], [67, 31]]
        self.assertEqual(output, expected_output_points)

    def testConvertWithDefaultParam(self):
        config.X_PIXELS_TO_MILLIMETRE_SCALE = 4
        config.Y_PIXELS_TO_MILLIMETRE_SCALE = 4
        config.CAMERA_RESOLUTION = (200, 200)
        points = [(0, 100), (13, 120), (85, 122), (27, 128), (150, 130)]
        centre = (50, 40)

        scan_direction = image_analysis_enums.Direction.SOUTH
        output = roboplot.core.camera.camera_utils.convert_to_global_coords(points,
                                                                            scan_direction,
                                                                            centre,
                                                                            0,
                                                                            config.CAMERA_RESOLUTION[0] //2)

        expected_output_points = [[50, 40.0], [102, 120.0], [390, 128.0], [158, 152.0], [650, 160.0]]
        self.assertEqual(output, expected_output_points)


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
