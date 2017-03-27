#!/usr/bin/env python3

import unittest
import time
import math

import cv2
import numpy as np

import context
import roboplot.config as config
import roboplot.core.camera.camera_utils as camera_utils
import roboplot.imgproc.image_analysis as image_analysis


class CameraPathTranslationTest(unittest.TestCase):

    def testTranslatePoint(self):
        config.CAMERA_OFFSET = [2.33, 2.37]
        point = [[2.0, 10.0]]

        # Translate Point
        translated_point = camera_utils.translate_camera_points_to_global_points(point)
        expected_point = [4.33, 12.37]
        self.assertTrue(np.allclose(translated_point, expected_point, atol=1e-3))

    def testTranslateListOfPoints(self):
        config.CAMERA_OFFSET = [2.33, 2.37]
        points = [[2.0, 10], [3.0, 6.93], [5.78, 8.04], [36.9, 65.23], [34.33, 92.69]]

        # Translate Point
        translated_point = camera_utils.translate_camera_points_to_global_points(points)
        expected_point = [[4.33, 12.37], [5.33, 9.3], [8.11, 10.41], [39.23, 67.6], [36.66, 95.06]]
        self.assertTrue(np.allclose(translated_point, expected_point, atol=1e-3))

# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
