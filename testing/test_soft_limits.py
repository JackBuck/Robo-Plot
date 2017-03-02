#!/usr/bin/env python3

import os
import time
import unittest
import contextlib
import warnings
from io import StringIO

import numpy as np

import context
import roboplot.config as config
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware


class SoftLimitTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SoftLimitTest, self).__init__(*args, **kwargs)
        hardware.both_axes.home()

    def test_ExceedMinXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([1, 5], [1, hardware.both_axes.x_soft_lower_limit - 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMaxXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([1, 295], [1, hardware.both_axes.x_soft_upper_limit + 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMinYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([5, 1], [hardware.both_axes.y_soft_lower_limit - 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMaxYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([295, 1], [hardware.both_axes.x_soft_upper_limit + 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_TouchMinXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([1, 5], [1, hardware.both_axes.x_soft_lower_limit])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMaxXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([1, 295], [1, hardware.both_axes.x_soft_upper_limit])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMinYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([5, 1], [hardware.both_axes.x_soft_lower_limit, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMaxYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([295, 1], [hardware.both_axes.y_soft_upper_limit, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)
        
    def test_ExceedMinXLimit_LimitsOff(self):
        line_segment = curves.LineSegment([1, 5], [1, hardware.both_axes.x_soft_upper_limit - 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, False)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMaxXLimit_LimitsOff(self):
        line_segment = curves.LineSegment([1, 295], [1, hardware.both_axes.x_soft_upper_limit + 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, False)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMinYLimit_LimitsOff(self):
        line_segment = curves.LineSegment([5, 1], [hardware.both_axes.x_soft_upper_limit - 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, False)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMaxYLimit_LimitsOff(self):
        line_segment = curves.LineSegment([295, 1], [hardware.both_axes.y_soft_upper_limit + 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, False)
            # Verify warnings
            self.assertEqual(len(w), 0)

    @staticmethod
    def _test_soft_limit(curve, use_limits=True, suppress_warnings=False):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            hardware.both_axes.follow(curve, pen_speed=100, use_soft_limits=use_limits, suppress_limit_warnings=suppress_warnings)


def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
