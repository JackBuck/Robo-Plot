#!/usr/bin/env python3


import unittest
import time
import math

import cv2
import numpy as np

import context
import roboplot.imgproc.image_analysis as image_analysis

# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class RotationTest(unittest.TestCase):

    def testRotateAboutOrigin(self):
        origin = (0.0, 0.0)

        point = (2.0, 10)

        # Rotate 90 anti-clockwise
        angle = math.radians(90)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (-10, 2.0)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-3))

        # Rotate 90 clockwise
        angle = math.radians(-90)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (10, -2.0)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-3))

        # Rotate 45 anti-clockwise
        angle = math.radians(45)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (-5.656, 8.485)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-2))

        # Rotate 45 clockwise
        angle = math.radians(-45)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (8.485, 5.656)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-2))

    def testRotateAboutPoint(self):
        origin = (5.0, 8.0)
        point = (2.0, 10)

        # Rotate 90 anti-clockwise
        angle = math.radians(90)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (3.0, 5.0)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-3))

        # Rotate 90 clockwise
        angle = math.radians(-90)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (7.0, 11.0)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-3))

        # Rotate 45 anti-clockwise
        angle = math.radians(45)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (1.46, 7.29)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-2))

        # Rotate 45 clockwise
        angle = math.radians(-45)
        rotated_point = image_analysis.rotate(origin, point, angle)
        expected_point = (4.29, 11.54)
        self.assertTrue(np.allclose(rotated_point, expected_point, atol=1e-2))

# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
