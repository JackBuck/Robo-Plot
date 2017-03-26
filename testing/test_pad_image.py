#!/usr/bin/env python3

import os
import unittest
import time

import cv2
import numpy as np

import context
import roboplot.config as config
import roboplot.core.camera.camera_utils as camera_utils


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class PadImageTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(PadImageTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'PadImageTest')

    def test_pad_top(self):
        # Request new centre below current centre
        new_centre = (80, 100)

        # Pad Image Test.
        self.pad_test('pad_top', new_centre)

    def test_pad_bottom(self):
        # Request new centre below current centre
        new_centre = (120, 100)

        # Pad Image Test.
        self.pad_test('pad_bottom', new_centre)

    def test_pad_left(self):
        # Request new centre below current centre
        new_centre = (100, 20)

        # Pad Image Test.
        self.pad_test('pad_left', new_centre)

    def test_pad_right(self):
        # Request new centre below current centre
        new_centre = (100, 180)

        # Pad Image Test.
        self.pad_test('pad_right', new_centre)

    def test_pad_top_extreme(self):
        # Request new centre below current centre
        new_centre = (-60, 100)

        # Pad Image Test.
        self.pad_test('pad_top_extreme', new_centre)

    def test_pad_bottom_extreme(self):
        # Request new centre below current centre
        new_centre = (250, 100)

        # Pad Image Test.
        self.pad_test('pad_bottom_extreme', new_centre)

    def test_pad_left_extreme(self):
        # Request new centre below current centre
        new_centre = (100, -30)

        # Pad Image Test.
        self.pad_test('pad_left_extreme', new_centre)

    def test_pad_right_extreme(self):
        # Request new centre below current centre
        new_centre = (100, 230)

        # Pad Image Test.
        self.pad_test('pad_right_extreme', new_centre)

    def test_pad_top_left(self):
        # Request new centre below current centre
        new_centre = (50, 50)

        # Pad Image Test.
        self.pad_test('pad_top_left', new_centre)

    def test_pad_top_right(self):
        # Request new centre below current centre
        new_centre = (50, 150)

        # Pad Image Test.
        self.pad_test('pad_top_right', new_centre)

    def test_pad_bottom_left(self):
        # Request new centre below current centre
        new_centre = (150, 50)

        # Pad Image Test.
        self.pad_test('pad_bottom_left', new_centre)

    def test_pad_bottom_right(self):
        # Request new centre below current centre
        new_centre = (150, 150)

        # Pad Image Test.
        self.pad_test('bottom_right', new_centre)

    def test_centre(self):
        # Request new centre below current centre
        new_centre = (100, 100)

        # Pad Image Test.
        self.pad_test('bottom_right', new_centre)

        # Load image for testing.
        image = cv2.imread(os.path.join(self.path_to_test_data, 'pad_test_input.png'))
        image = cv2.resize(image, (200, 200))

        # Check image was loaded correctly
        if image is None:
            raise TypeError

        # Pad Image.
        modified_image = camera_utils.pad_image(image, new_centre)

        # Compare images
        self.assertTrue(not (np.bitwise_xor(modified_image, image).any()))

    def pad_test(self, filename_without_extension, new_centre):
        # Load image for testing.
        image = cv2.imread(os.path.join(self.path_to_test_data, 'pad_test_input.png'))
        image = cv2.resize(image, (200, 200))

        # Check image was loaded correctly
        if image is None:
            raise TypeError

        # Pad Image.
        modified_image = camera_utils.pad_image(image, new_centre)

        # This has to be done with png.
        expected_results_file = os.path.join(self.path_to_test_data, filename_without_extension + '_expected.png')
        #self._overwrite_expected_results_file(expected_results_file, modified_image)

        # Load expected image
        expected_image = cv2.imread(expected_results_file)

        # Compare images
        self.assertTrue(not(np.bitwise_xor(modified_image, expected_image).any()))

    @staticmethod
    def _overwrite_expected_results_file(expected_results_file, modified_image):
        # Save image.
        cv2.imwrite(expected_results_file, modified_image)

# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
