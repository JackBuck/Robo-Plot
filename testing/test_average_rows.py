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
        self.averageRowsWithRotationTest('straight')

    def test_right_tilted_angle(self):
        self.averageRowsTest('right_tilted_angle')
        self.averageRowsWithRotationTest('right_tilted_angle')

    def test_left_tilted_angle(self):
        self.averageRowsTest('left_tilted_angle')
        self.averageRowsWithRotationTest('left_tilted_angle')

    def test_right_angle_left(self):
        self.averageRowsTest('right_angle_left')
        self.averageRowsWithRotationTest('right_angle_left')

    def test_right_angle_right(self):
        self.averageRowsTest('right_angle_right')
        self.averageRowsWithRotationTest('right_angle_right')

    #def test_acute_angle_left(self):
        # self.averageRowsTest('acute_angle_left') # Questionable result
        # self.averageRowsWithRotationTest('acute_angle_left')

    #def test_acute_angle_right(self):
        # self.averageRowsTest('acute_angle_right') # Questionable result
        # self.averageRowsWithRotationTest('acute_angle_right')

    def test_curve_left(self):
        self.averageRowsTest('curve_left')
        self.averageRowsWithRotationTest('curve_left')

    def test_curve_right(self):
        self.averageRowsTest('curve_right')
        self.averageRowsWithRotationTest('curve_right')

    def test_u_turn_left(self):
        self.averageRowsTest('u_turn_left')
        self.averageRowsWithRotationTest('u_turn_left')

    def test_u_turn_right(self):
        self.averageRowsTest('u_turn_right')
        self.averageRowsWithRotationTest('u_turn_right')

    def averageRowsTest(self, filename_without_extension):
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'))

        if image is None:
            raise TypeError

        image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        image = cv2.resize(image, (200, 100))
        search_width = 100
        start_time = time.time()
        pixel_indices, turn = image_analysis.analyse_rows(image, search_width, is_rotated=False)
        end_time = time.time()

        print('Time Taken for average rows:' + filename_without_extension + ': ' + str(end_time - start_time))

        expected_results_file = os.path.join(self.path_to_test_data, 'expected_' + filename_without_extension + '.csv')

        # debug_sub_image = iadebug.save_average_rows(image, pixel_indices)
        # self._overwrite_expected_results_file(expected_results_file, pixel_indices)  # For creating test data

        expected_averages = np.loadtxt(expected_results_file, delimiter=",")
        self.assertTrue(np.array_equal(pixel_indices, expected_averages),
                        msg="Actual=\n{}\nExpected=\n{}".format(np.array(pixel_indices), expected_averages))

    def averageRowsWithRotationTest(self, filename_without_extension):
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'))

        if image is None:
            raise TypeError

        image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        image = cv2.resize(image, (200, 100))
        search_width = 100
        start_time = time.time()
        pixel_indices, turn_to_next_scan = image_analysis.analyse_rows(image, search_width, is_rotated=False)
        if (len(pixel_indices) < image.shape[0]) and (turn_to_next_scan is not image_analysis.Turning.STRAIGHT):

            if turn_to_next_scan is image_analysis.Turning.LEFT:
                angle = -60
            else:
                angle = 60

            # Create rotated sub_image to analyse
            sub_image = image_analysis.create_rotated_sub_image(image, pixel_indices[-1], search_width, angle)

            # Analyse sub image
            rotated_indices, turn_to_next_scan = image_analysis.analyse_rows(sub_image, search_width, is_rotated=True)

            # Rotate line indices back.
            extra_indices = [list(map(operator.add,
                                  (int(pixel_indices[-1][0]), int(pixel_indices[-1][1] - sub_image.shape[1] / 2)),
                                  image_analysis.rotate(rotated_indices[0], point, math.radians(-angle))))
                             for point in rotated_indices]

            pixel_indices += extra_indices

        end_time = time.time()
        print('Time Taken for average rows with rotation:' + filename_without_extension + ': ' + str(end_time - start_time))

        expected_results_file = os.path.join(self.path_to_test_data,
                                             'expected_rotated_' + filename_without_extension + '.csv')

        # debug_sub_image = iadebug.save_average_rows(image, pixel_indices)
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
