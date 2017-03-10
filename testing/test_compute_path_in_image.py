#!/usr/bin/env python3


import unittest
import time
import os

import cv2

import context
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class PathFromImageTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(PathFromImageTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'PathFromImageTest')

    def testSouth(self):
        # Load image for testing.
        image = cv2.imread(os.path.join(self.path_to_test_data, 'South.jpg'), cv2.IMREAD_GRAYSCALE)

        # Check image was loaded correctly
        if image is None:
            raise TypeError

        # Calculate points from image.
        pixel_points = image_analysis.compute_pixel_points(image)
        expected_pixel_points = [(100, 0), (100, 99)]
        self.assertEqual(pixel_points, expected_pixel_points)

# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
