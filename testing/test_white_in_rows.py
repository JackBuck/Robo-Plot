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
import roboplot.imgproc.path_following as path_following


class WhiteInRows(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(WhiteInRows, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'WhiteInRows')

    def test_no_white(self):
        white_found_near_centre = self.whiteRowsTest('no_white')
        self.assertFalse(white_found_near_centre[0])
        self.assertFalse(white_found_near_centre[1])
        self.assertFalse(white_found_near_centre[2])
        self.assertFalse(white_found_near_centre[3])

    def test_white_not_central(self):
        white_found_near_centre = self.whiteRowsTest('white_not_central')
        self.assertTrue(white_found_near_centre[0])
        self.assertTrue(white_found_near_centre[1])
        self.assertTrue(white_found_near_centre[2])
        self.assertTrue(white_found_near_centre[3])

    def test_white_central(self):
        white_found_near_centre = self.whiteRowsTest('white_central')
        self.assertTrue(white_found_near_centre[0])
        self.assertTrue(white_found_near_centre[1])
        self.assertTrue(white_found_near_centre[2])
        self.assertTrue(white_found_near_centre[3])

    def test_white_not_both_directions(self):
        white_found_near_centre = self.whiteRowsTest('white_not_both_directions')
        self.assertFalse(white_found_near_centre[0])
        self.assertTrue(white_found_near_centre[1])
        self.assertFalse(white_found_near_centre[2])
        self.assertTrue(white_found_near_centre[3])

    def whiteRowsTest(self, filename_without_extension):
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.png'))

        if image is None:
            raise TypeError

        image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

        start_time = time.time()
        white_found_near_centre = path_following.PathFinder.white_found_near_centre(search_width=30,
                                                                                    image_to_analyse=image)
        end_time = time.time()

        print('Time Taken for average rows:' + filename_without_extension + ': ' + str(end_time - start_time))

        return white_found_near_centre

def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
