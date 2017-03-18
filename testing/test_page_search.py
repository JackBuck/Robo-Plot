#!/usr/bin/env python3


import unittest
import time

import cv2
import numpy as np

import context
import roboplot.imgproc.colour_detection as cd
import roboplot.imgproc.page_search as page_search


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class PageSearchTest(unittest.TestCase):

    def testPageSearch(self):
        a4_width_x_mm = 210
        a4_height_y_mm = 297
        photo_size_mm = 40
        camera_positions = page_search.compute_positions(a4_width_x_mm, a4_height_y_mm, photo_size_mm)
        expected_positions = [[20, 20], [20, 60], [20, 100], [20, 140], [20, 180], [20, 190], [60, 190], [60, 150], [60, 110], [60, 70], [60, 30], [60, 20], [100, 20], [100, 60], [100, 100], [100, 140], [100, 180], [100, 190], [140, 190], [140, 150], [140, 110], [140, 70], [140, 30], [140, 20], [180, 20], [180, 60], [180, 100], [180, 140], [180, 180], [180, 190], [220, 190], [220, 150], [220, 110], [220, 70], [220, 30], [220, 20], [260, 20], [260, 60], [260, 100], [260, 140], [260, 180], [260, 190], [277, 190], [277, 150], [277, 110], [277, 70], [277, 30], [277, 20]]
        self.assertEqual(camera_positions, expected_positions)

# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
