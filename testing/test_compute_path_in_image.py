#!/usr/bin/env python3


import unittest
import time
import os

import cv2
import numpy as np

import context
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.image_analysis_debug as iadebug


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class PathFromImageTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(PathFromImageTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'PathFromImageTest')

    def test_straight(self):
        turn_to_next_scan = self.computePathFromImage('straight')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.STRAIGHT)

    def test_right_tilted_angle(self):
        turn_to_next_scan = self.computePathFromImage('right_tilted_angle')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.STRAIGHT)

    def test_left_tilted_angle(self):
        turn_to_next_scan = self.computePathFromImage('left_tilted_angle')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.STRAIGHT)

    def test_right_angle_left(self):
        turn_to_next_scan = self.computePathFromImage('right_angle_left')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.LEFT)

    def test_right_angle_right(self):
        turn_to_next_scan = self.computePathFromImage('right_angle_right')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.RIGHT)

    def test_acute_angle_left(self):
        turn_to_next_scan = self.computePathFromImage('acute_angle_left')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.LEFT)

    def test_acute_angle_right(self):
            turn_to_next_scan = self.computePathFromImage('acute_angle_right')
            self.assertEqual(turn_to_next_scan, image_analysis.Turning.RIGHT)

    def test_curve_left(self):
        turn_to_next_scan = self.computePathFromImage('curve_left')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.LEFT)

    def test_curve_right(self):
        turn_to_next_scan = self.computePathFromImage('curve_right')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.RIGHT)

    def test_u_turn_left(self):
        turn_to_next_scan = self.computePathFromImage('u_turn_left')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.LEFT)

    def test_u_turn_right(self):
        turn_to_next_scan = self.computePathFromImage('u_turn_right')
        self.assertEqual(turn_to_next_scan, image_analysis.Turning.RIGHT)

    def computePathFromImage(self, filename_without_extension):
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'))

        if image is None:
            raise TypeError

        image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        image = cv2.resize(image, (200, 100))
        search_width = 100
        start_time = time.time()
        pixel_path, turn_to_next_scan = image_analysis.compute_pixel_path(image, search_width)
        end_time = time.time()

        print('Time Taken to compute pixel path:' + filename_without_extension + ': ' + str(end_time - start_time))

        expected_results_file = os.path.join(self.path_to_test_data,
                                             'expected_pixel_path_' + filename_without_extension + '.csv')

        debug_sub_image = iadebug.create_debug_image(image)
        iadebug.save_line_approximation(debug_sub_image, pixel_path, False)
        # self._overwrite_expected_results_file(expected_results_file, pixel_path)  # For creating test data

        expected_pixel_path = np.loadtxt(expected_results_file, delimiter=",")
        self.assertTrue(np.array_equal(pixel_path, expected_pixel_path),
                        msg="Actual=\n{}\nExpected=\n{}".format(np.array(pixel_path), expected_pixel_path))

        return turn_to_next_scan

    @staticmethod
    def _overwrite_expected_results_file(expected_results_file, pixel_indices):
        # Save point to integer points, this stops most small numerical changes from causing the tests to fail.
        np.savetxt(expected_results_file, pixel_indices, fmt='%d', delimiter=",")
def main():
    unittest.main()


if __name__ == '__main__':
    main()
