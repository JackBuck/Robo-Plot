#!/usr/bin/env python3

import unittest
import contextlib
import warnings
from io import StringIO

import context
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware
import roboplot.core.limit_switches as limit_switches
from roboplot.core.stepper_control import Axis


def _setup_small_axis_travels():
    # TODO: This is less than ideal because this method may need to change if we update the PretendLimitSwitch (a
    # hidden dependence). But I've spent too long on this already!
    x_limit_switches = limit_switches.define_pretend_limit_switches(hardware.x_home_position, separation=5)
    _replace_limit_switches_on_axis(hardware.x_axis, x_limit_switches)

    y_limit_switches = limit_switches.define_pretend_limit_switches(hardware.y_home_position, separation=5)
    _replace_limit_switches_on_axis(hardware.y_axis, y_limit_switches)


def _replace_limit_switches_on_axis(axis: Axis, switches):
    for i in (0, 1):
        axis.limit_switches[i].valid_range = switches[i].valid_range


def _set_current_location_between_switches():
    hardware.x_axis.current_location = hardware.x_limit_switches[0].get_location_infront_of_switch(millimetres=2.5)
    hardware.y_axis.current_location = hardware.y_limit_switches[0].get_location_infront_of_switch(millimetres=2.5)


class SoftLimitTest(unittest.TestCase):

    def setUp(self):
        _setup_small_axis_travels()
        _set_current_location_between_switches()
        hardware.both_axes.home()

    def test_ExceedMinXLimit_LimitsOn(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_lower_limit + 1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_lower_limit + 1], [1, hardware.both_axes.x_soft_lower_limit - 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMaxXLimit_LimitsOn(self):
        hardware.x_axis.current_location = hardware.both_axes.x_soft_upper_limit - 1
        target_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_upper_limit + 1)
        line_segment = curves.LineSegment(hardware.both_axes.current_location, target_location)
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMinYLimit_LimitsOn(self):
        hardware.both_axes.current_location = (hardware.both_axes.y_soft_lower_limit + 1, 1)
        line_segment = curves.LineSegment([hardware.both_axes.y_soft_lower_limit + 1, 1], [hardware.both_axes.y_soft_lower_limit - 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_ExceedMaxYLimit_LimitsOn(self):
        hardware.both_axes.current_location = (hardware.both_axes.x_soft_upper_limit - 1, 1)
        line_segment = curves.LineSegment([hardware.both_axes.x_soft_upper_limit - 1, 1], [hardware.both_axes.x_soft_upper_limit + 1, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test.
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_TouchMinXLimit_LimitsOn(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_lower_limit + 1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_lower_limit + 1], [1, hardware.both_axes.x_soft_lower_limit])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMaxXLimit_LimitsOn(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_upper_limit - 1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_upper_limit - 1], [1, hardware.both_axes.x_soft_upper_limit])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMinYLimit_LimitsOn(self):
        hardware.both_axes.current_location = (hardware.both_axes.x_soft_lower_limit + 1, 1)
        line_segment = curves.LineSegment([hardware.both_axes.x_soft_lower_limit + 1, 1], [hardware.both_axes.x_soft_lower_limit, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)

    def test_TouchMaxYLimit_LimitsOn(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_upper_limit -1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_upper_limit - 1], [hardware.both_axes.y_soft_upper_limit, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            self._test_soft_limit(line_segment, True)
            # Verify warnings
            self.assertEqual(len(w), 0)
        
    def test_ExceedMinXLimit_SoftLimitsOff(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_lower_limit + 1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_lower_limit + 1], [1, hardware.both_axes.x_soft_lower_limit - 10])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            with self.assertRaises(limit_switches.UnexpectedLimitSwitchError):
                self._test_soft_limit(line_segment, False)

            # Verify no warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMaxXLimit_SoftLimitsOff(self):
        hardware.both_axes.current_location = (1, hardware.both_axes.x_soft_upper_limit - 1)
        line_segment = curves.LineSegment([1, hardware.both_axes.x_soft_upper_limit - 1], [1, hardware.both_axes.x_soft_upper_limit + 10])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            with self.assertRaises(limit_switches.UnexpectedLimitSwitchError):
                self._test_soft_limit(line_segment, False)

            # Verify no warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMinYLimit_SoftLimitsOff(self):
        hardware.both_axes.current_location = (hardware.both_axes.x_soft_upper_limit + 1, 1)
        line_segment = curves.LineSegment([hardware.both_axes.x_soft_upper_limit + 1, 1], [hardware.both_axes.x_soft_upper_limit - 10, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            with self.assertRaises(limit_switches.UnexpectedLimitSwitchError):
                self._test_soft_limit(line_segment, False)

            # Verify no warnings
            self.assertEqual(len(w), 0)

    def test_ExceedMaxYLimit_SoftLimitsOff(self):
        hardware.both_axes.current_location = (hardware.both_axes.y_soft_upper_limit - 1, 1)
        line_segment = curves.LineSegment([hardware.both_axes.y_soft_upper_limit - 1, 1], [hardware.both_axes.y_soft_upper_limit + 10, 1])
        with warnings.catch_warnings(record=True) as w:
            # Run test
            with self.assertRaises(limit_switches.UnexpectedLimitSwitchError):
                self._test_soft_limit(line_segment, False)

            # Verify no warnings
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
