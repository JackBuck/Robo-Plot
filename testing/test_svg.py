#!/usr/bin/env python3

import os
import time
import unittest

import numpy as np

import context
import roboplot.config as config
import roboplot.svg.svg_parsing as svg


class SVGTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SVGTest, self).__init__(*args, **kwargs)
        self.path_to_test_data = os.path.join(config.test_data_dir, 'SVGTest')
        self.millimetres_per_linear_interval = 1

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

    def svgToPathTest(self, filename_without_extension):
        start_time = time.time()
        total_points = self._convert_to_points(filename_without_extension + '.svg')
        end_time = time.time()
        print('Time Taken for ' + filename_without_extension + ': ' + str(end_time - start_time))

        total_points_array = np.asarray(total_points)

        expected_results_file = os.path.join(self.path_to_test_data, 'expected_' + filename_without_extension + '.txt')
        # self._overwrite_expected_results_file(expected_results_file, total_points_array)  # For creating test data
        expected_points = np.loadtxt(expected_results_file)

        self.assertTrue(np.allclose(total_points_array, expected_points, atol=2e-1))

    @staticmethod
    def _overwrite_expected_results_file(expected_results_file, total_points_array):
        # Save point to 5 decimal points, this stops most small numerical changes from causing the tests to fail.
        np.savetxt(expected_results_file, total_points_array, fmt='%.5f')

    def _convert_to_points(self, filename):
        svg_curves = svg.parse(os.path.join(self.path_to_test_data, filename))

        total_points = []
        for curve in svg_curves:
            points = curve.to_series_of_points(self.millimetres_per_linear_interval)
            total_points += np.ndarray.tolist(points)

        return total_points


def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
