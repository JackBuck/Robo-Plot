#!/usr/bin/env python3

import os
import unittest
import time

import cv2

import context
import roboplot.config as config
import roboplot.imgproc.colour_detection as cd


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class ColourDetectionTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ColourDetectionTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'ColourDetectionTest')

    def testGreenDetection(self):
        # Load image for testing.
        image = cv2.imread(os.path.join(self.path_to_test_data, 'testGreenDetection.jpg'))

        # Check image was loaded correctly
        if image is None:
            raise TypeError

        # Convert image to hsv image.
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Declare minimum size.
        MIN_SIZE = 10

        # Find green in image.
        (cX, cY) = cd.detect_green(hsv_image, MIN_SIZE, False)

        # Declare expected values.
        EXPECTED_CX = 381
        EXPECTED_CY = 493
        self.assertEqual(cX, EXPECTED_CX)
        self.assertEqual(cY, EXPECTED_CY)

    def testRedDetection(self):
        # Load image for testing.
        image = cv2.imread(os.path.join(self.path_to_test_data, 'testRedDetection.jpg'))

        # Check image was loaded correctly
        if image is None:
            raise TypeError

        # Convert image to hsv image.
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Declare minimum size.
        MIN_SIZE = 10

        # Find green in image.
        (cX, cY) = cd.detect_red(hsv_image, MIN_SIZE, False)

        # Declare expected values.
        EXPECTED_CX = 177
        EXPECTED_CY = 443
        self.assertEqual(cX, EXPECTED_CX)
        self.assertEqual(cY, EXPECTED_CY)


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
