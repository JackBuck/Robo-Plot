#!/usr/bin/env python3

import os
import time
import unittest
import math
import operator

import numpy as np
import cv2

import context
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.image_analysis_debug as iadebug


class AverageRowsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AverageRowsTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'AverageRowsTest')

    def test_straight(self):
        self.averageRowsTest('straight')

    def test_right_tilted_angle(self):
        self.averageRowsTest('right_tilted_angle')

    def test_left_tilted_angle(self):
        self.averageRowsTest('left_tilted_angle')

    def test_right_angle_left(self):
        self.averageRowsTest('right_angle_left')

    def test_right_angle_right(self):
        self.averageRowsTest('right_angle_right')

    def test_acute_angle_left(self):
        self.averageRowsTest('acute_angle_left')

    def test_acute_angle_right(self):
        self.averageRowsTest('acute_angle_right')

    def test_curve_left(self):
        self.averageRowsTest('curve_left')

    def test_curve_right(self):
        self.averageRowsTest('curve_right')

    def test_u_turn_left(self):
        self.averageRowsTest('u_turn_left')

    def test_u_turn_right(self):
        self.averageRowsTest('u_turn_right')

    @unittest.skip
    def test_right_angle_left_rotated_image(self):
        self.averageRowsTest('right_angle_left_rotated_example')

    @unittest.skip
    def test_right_angle_right_rotated_image(self):
        self.averageRowsTest('right_angle_right_rotated_example')

    @unittest.skip
    def test_curve_left_rotated_image(self):
        self.averageRowsTest('curve_left_rotated_example')

    @unittest.skip
    def test_curve_right_rotated_image(self):
        self.averageRowsTest('curve_right_rotated_example')

    @unittest.skip
    def test_u_turn_left_rotated_image(self):
        self.averageRowsTest('u_turn_left_rotated_example')

    @unittest.skip
    def test_u_turn_right_rotated_image(self):
        self.averageRowsTest('u_turn_right_rotated_example')

    def averageRowsTest(self, filename_without_extension):
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'))

        if image is None:
            raise TypeError

        image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

        # Resize image to have width of 200.

        resize_ratio = 100/image.shape[1]
        image = cv2.resize(image, (0, 0), fx=resize_ratio, fy=resize_ratio)
        search_width = 100
        start_time = time.time()
        pixel_indices, turn = image_analysis.analyse_rows(image, search_width, is_rotated=False)
        end_time = time.time()

        print('Time Taken for average rows:' + filename_without_extension + ': ' + str(end_time - start_time))

        expected_results_file = os.path.join(self.path_to_test_data, 'expected_' + filename_without_extension + '.csv')

        # debug_sub_image = iadebug.save_average_rows(image, pixel_indices, False)
        # self._overwrite_expected_results_file(expected_results_file, pixel_indices)  # For creating test data

        expected_averages = np.loadtxt(expected_results_file, delimiter=",")
        self.assertTrue(np.array_equal(pixel_indices, expected_averages),
                        msg="Actual=\n{}\nExpected=\n{}".format(np.array(pixel_indices), expected_averages))

    @staticmethod
    def _overwrite_expected_results_file(expected_results_file, pixel_indices):
        # Save point to integer points, this stops most small numerical changes from causing the tests to fail.
        np.savetxt(expected_results_file, pixel_indices, fmt='%d', delimiter=",")


def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
