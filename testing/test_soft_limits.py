#!/usr/bin/env python3

import unittest
import warnings

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
        hardware.plotter.home()

    def test_exceeding_min_x_soft_limit_raises_warning_when_limits_are_on(self):
        line_segment = self._build_segment_crossing_min_x_soft_limit()
        self._follow_line_and_assert_soft_limit_warning(line_segment)

    def test_exceeding_max_x_soft_limit_raises_warning_when_limits_are_on(self):
        line_segment = self._build_segment_crossing_max_x_soft_limit()
        self._follow_line_and_assert_soft_limit_warning(line_segment)

    def test_exceeding_min_y_soft_limit_raises_warning_when_limits_are_on(self):
        line_segment = self._build_segment_crossing_min_y_soft_limit()
        self._follow_line_and_assert_soft_limit_warning(line_segment)

    def test_exceeding_max_y_soft_limit_raises_warning_when_limits_are_on(self):
        line_segment = self._build_segment_crossing_max_y_soft_limit()
        self._follow_line_and_assert_soft_limit_warning(line_segment)

    def _follow_line_and_assert_soft_limit_warning(self, line_segment):
        hardware.current_location = line_segment.start

        with warnings.catch_warnings(record=True) as w:

            hardware.both_axes.follow(line_segment, pen_speed=100, use_soft_limits=True, suppress_limit_warnings=False)

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue("Part of the curve lay outside of the soft limits" in str(w[-1].message))

    def test_touching_min_x_soft_limit_does_not_raise_warning_when_limits_are_on(self):
        line_segment = self._build_segment_touching_min_x_soft_limit()
        self._follow_line_and_assert_no_warning(line_segment)

    def test_touching_max_x_soft_limit_does_not_raise_warning_when_limits_are_on(self):
        line_segment = self._build_segment_touching_max_x_soft_limit()
        self._follow_line_and_assert_no_warning(line_segment)

    def test_touching_min_y_soft_limit_does_not_raise_warning_when_limits_are_on(self):
        line_segment = self._build_segment_touching_min_y_soft_limit()
        self._follow_line_and_assert_no_warning(line_segment)

    def test_touching_max_y_soft_limit_does_not_raise_warning_when_limits_are_on(self):
        line_segment = self._build_segment_touching_max_x_soft_limit()
        self._follow_line_and_assert_no_warning(line_segment)

    def _follow_line_and_assert_no_warning(self, line_segment):
        hardware.current_location = line_segment.start
        with warnings.catch_warnings(record=True) as w:
            hardware.both_axes.follow(line_segment, pen_speed=100, use_soft_limits=True, suppress_limit_warnings=False)
            self.assertEqual(len(w), 0)

    @staticmethod
    def _build_segment_touching_min_x_soft_limit():
        start_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_lower_limit + 1)
        target_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_lower_limit)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_touching_max_x_soft_limit():
        start_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_upper_limit - 1)
        target_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_upper_limit)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_touching_min_y_soft_limit():
        start_location = (hardware.both_axes.y_soft_lower_limit + 1, hardware.x_axis.current_location)
        target_location = (hardware.both_axes.y_soft_lower_limit, hardware.x_axis.current_location)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_touching_max_y_soft_limit():
        start_location = (hardware.both_axes.y_soft_upper_limit - 1, hardware.x_axis.current_location)
        target_location = (hardware.both_axes.y_soft_upper_limit, hardware.x_axis.current_location)
        return curves.LineSegment(start_location, target_location)

    def test_exceeding_min_x_soft_limit_does_not_raise_warning_when_limits_are_off(self):
        line_segment = self._build_segment_crossing_min_x_soft_limit()
        self._follow_line_with_soft_limits_off_and_assert_no_warning(line_segment)

    def test_exceeding_max_x_soft_limit_does_not_raise_warning_when_limits_are_off(self):
        line_segment = self._build_segment_crossing_max_x_soft_limit()
        self._follow_line_with_soft_limits_off_and_assert_no_warning(line_segment)

    def test_exceeding_min_y_soft_limit_does_not_raise_warning_when_limits_are_off(self):
        line_segment = self._build_segment_crossing_min_y_soft_limit()
        self._follow_line_with_soft_limits_off_and_assert_no_warning(line_segment)

    def test_exceeding_max_y_soft_limit_does_not_raise_warning_when_limits_are_off(self):
        line_segment = self._build_segment_crossing_max_y_soft_limit()
        self._follow_line_with_soft_limits_off_and_assert_no_warning(line_segment)

    def _follow_line_with_soft_limits_off_and_assert_no_warning(self, line_segment):
        hardware.current_location = line_segment.start
        with warnings.catch_warnings(record=True) as w:
            try:
                hardware.both_axes.follow(line_segment, pen_speed=100, use_soft_limits=False, suppress_limit_warnings=False)
            except limit_switches.UnexpectedLimitSwitchError:
                pass

            self.assertEqual(len(w), 0)

    @staticmethod
    def _build_segment_crossing_min_x_soft_limit():
        start_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_lower_limit + 1)
        target_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_lower_limit - 1)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_crossing_max_x_soft_limit():
        start_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_upper_limit - 1)
        target_location = (hardware.y_axis.current_location, hardware.both_axes.x_soft_upper_limit + 1)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_crossing_min_y_soft_limit():
        start_location = (hardware.both_axes.y_soft_lower_limit + 1, hardware.x_axis.current_location)
        target_location = (hardware.both_axes.y_soft_lower_limit - 1, hardware.x_axis.current_location)
        return curves.LineSegment(start_location, target_location)

    @staticmethod
    def _build_segment_crossing_max_y_soft_limit():
        start_location = (hardware.both_axes.y_soft_upper_limit - 1, hardware.x_axis.current_location)
        target_location = (hardware.both_axes.y_soft_upper_limit + 1, hardware.x_axis.current_location)
        return curves.LineSegment(start_location, target_location)


def main():
    """Running this runs all the tests and outputs their results."""
    unittest.main()


if __name__ == '__main__':
    main()
