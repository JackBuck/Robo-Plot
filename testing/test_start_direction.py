#!/usr/bin/env python3

import os
import time
import unittest

import cv2

import context
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis


class StartDirectionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StartDirectionTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'StartDirectionTest')

    def test_North(self):
        start_direction = self.startDirectionTest('north')
        self.assertEqual(start_direction, image_analysis.Direction.NORTH)

    def test_East(self):
        start_direction = self.startDirectionTest('east')
        self.assertEqual(start_direction, image_analysis.Direction.EAST)

    def test_South(self):
        start_direction = self.startDirectionTest('south')
        self.assertEqual(start_direction, image_analysis.Direction.SOUTH)
 
    def test_West(self):
        start_direction = self.startDirectionTest('west')
        self.assertEqual(start_direction, image_analysis.Direction.WEST)

    def test_NorthNorthEast(self):
        start_direction = self.startDirectionTest('northnortheast')
        # Note that this is not the optimum result but the process should be able to handdle it.
        # If not the method will need to be revisited
        self.assertEqual(start_direction, image_analysis.Direction.EAST)

    def test_EastNorthEast(self):
        start_direction = self.startDirectionTest('eastnortheast')
        # Note that this is not the optimum result but the process should be able to handdle it.
        # If not the method will need to be revisited
        self.assertEqual(start_direction, image_analysis.Direction.NORTH)

    def test_CurveSouthWest(self):
        start_direction = self.startDirectionTest('curvesouthwest')
        self.assertEqual(start_direction, image_analysis.Direction.SOUTH)

    def test_CurveWestSouth(self):
        start_direction = self.startDirectionTest('curvewestsouth')
        self.assertEqual(start_direction, image_analysis.Direction.WEST)

    def startDirectionTest(self, filename_without_extension):
        # Load image
        image = cv2.imread(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'), cv2.IMREAD_GRAYSCALE)
        print(os.path.join(self.path_to_test_data, filename_without_extension + '.jpg'))
        
        if image is None:
            raise TypeError
        
        # Start timer
        start_time = time.time()
        
        # Process image for start.
        start_direction = image_analysis.find_start_direction(image)
        
        # Print time taken.
        end_time = time.time()
        print('Time Taken for ' + filename_without_extension + ': ' + str(end_time - start_time))

        return start_direction



def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
