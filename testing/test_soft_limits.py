#!/usr/bin/env python3

import os
import time
import unittest
import contextlib
from io import StringIO

import numpy as np

import context
import roboplot.config as config
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware


class SoftLimitTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SoftLimitTest, self).__init__(*args, **kwargs)

    def test_ExceedMinXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [100, -1])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == 'Warning: Part of the curve lay outside of the soft limits'

    def test_ExceedMaxXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [100, 300])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == 'Warning: Part of the curve lay outside of the soft limits'

    def test_ExceedMinYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [-1, 100])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == 'Warning: Part of the curve lay outside of the soft limits'

    def test_ExceedMaxYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [300, 100])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == 'Warning: Part of the curve lay outside of the soft limits'
        
    def test_TouchMinXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [100, 0])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == ''

    def test_TouchMaxXLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [100, hardware.both_axes.x_soft_limit])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == ''

    def test_TouchMinYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [0, 100])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == ''

    def test_TouchMaxYLimit_LimitsOn(self):
        line_segment = curves.LineSegment([100, 100] , [hardware.both_axes.y_soft_limit, 100])        
        console_output = self._test_soft_limit(line_segment)
        assert console_output == ''
        
    def test_ExceedMinXLimit_LimitsOff(self):
        line_segment = curves.LineSegment([100, 100] , [100, -1])        
        console_output = self._test_soft_limit(line_segment, False)
        assert console_output == ''

    def test_ExceedMaxXLimit_LimitsOff(self):
        line_segment = curves.LineSegment([100, 100] , [100, 300])        
        console_output = self._test_soft_limit(line_segment, False)
        assert console_output == ''

    def test_ExceedMinYLimit_LimitsOff(self):
        line_segment = curves.LineSegment([100, 100] , [-1, 100])        
        console_output = self._test_soft_limit(line_segment, False)

    def test_ExceedMaxYLimit_LimitsOff(self):
        line_segment = curves.LineSegment([100, 100] , [300, 100])        
        console_output = self._test_soft_limit(line_segment, False)
        self.assertEqual(console_output,'')
        
    @staticmethod
    def _test_soft_limit(curve, use_limits=True, suppress_warnings=False):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            hardware.both_axes.follow(curve, pen_speed=30, use_soft_limits=use_limits, suppress_limit_warnings=suppress_warnings)
        output = temp_stdout.getvalue().strip()
        print(output)
        return output

 

def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
