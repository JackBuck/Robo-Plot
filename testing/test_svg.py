#!/usr/bin/env python3

import time
import unittest
import cv2
import numpy as np

import context
import roboplot.core.hardware as hardware
import roboplot.svg.svg_parsing as svg

# noinspection PyUnresolvedReferences
# import test_runner

class SVGTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SVGTest, self).__init__(*args, **kwargs)
        self.file_path = '../resources/test_data/SVGTest/'
        
    def svgToPathTest(self, filename):
        #Import svg
        svg_curves = svg.parse(self.file_path + filename + ".svg")
        
        INTERVAL_MILLIMETRES = 1
        

        total_points = []
        for curve in svg_curves:
            try:
                points = curve.to_series_of_points(INTERVAL_MILLIMETRES)
                total_points += np.ndarray.tolist(points)
            except:
                pass
                  
        total_points_array = np.asarray(total_points)
        
        # Save point to 5 decimal points, this stops most small numerical changes from causing the 
        # tests to fail. This line should be commented out except for when generating the expected
        # test data.
        np.savetxt(self.file_path + 'expected_' + filename +'.txt', total_points_array, fmt='%.5f')
        expected_path = np.loadtxt(self.file_path + 'expected_' + filename +'.txt')
        
        self.assertTrue(np.allclose(total_points_array,expected_path, atol=1e-3))
        
    def test_ArcToPath(self):
        self.svgToPathTest('arc')
        
    def test_ClosedArcAndLineToPath(self):
        self.svgToPathTest('closedArcAndLine')
        
    def test_CubeBezierPath(self):
        self.svgToPathTest('cubeBezier')
        
    def test_DiagonalLineToPath(self):
        self.svgToPathTest('diagonalLine')
        
    def test_HackSpaceSample(self):
        self.svgToPathTest('hackspaceSample')
        
    def test_QuadBezier(self):
        self.svgToPathTest('quadBezier')
        
    def test_StickFigBezier(self):
        self.svgToPathTest('stickFigBezier')
        
    def test_StraightLineToPath(self):
        self.svgToPathTest('straightLine')
              
 

# Running this runs all the tests and outputs their results.
def main():
    #unittest.main(testRunner=test_runner.CustomTestRunner())
    unittest.main()


if __name__ == '__main__':
    main()