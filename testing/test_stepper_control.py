#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock

import context
import roboplot.core.home_position
import roboplot.core.stepper_control as stepper_control
from roboplot.core.limit_switches import LimitSwitch, UnexpectedLimitSwitchError
from roboplot.core.stepper_motors import StepperMotor


class BaseTestCases:
    """
    A namespace for classes to be used as parent classes for test classes.

    The default test discovery system only looks inside module level classes deriving from unittest.TestCase.
    Therefore, classes defined inside this BaseTestCases class will not be found.
    """

    class Axis(unittest.TestCase):
        def setUp(self):
            self._mock_limit_switches = (MagicMock(name='switch_1', spec_set=LimitSwitch, is_pressed=False),
                                         MagicMock(name='switch_2', spec_set=LimitSwitch, is_pressed=False))
            self._mock_motor = MagicMock(name='motor', spec_set=StepperMotor, steps_per_revolution=200, clockwise=True)
            self._axis = stepper_control.Axis(self._mock_motor, 8, self._mock_limit_switches,
                                              roboplot.core.home_position.HomePosition(forwards=False, location=0))


class AxisStepTests(BaseTestCases.Axis):
    """Tests the behaviour of the Axis.step() method."""

    def test_stepping_does_not_raise_when_no_limit_switch_is_pressed(self):
        self._axis.step()

    def test_advances_no_further_when_a_limit_switch_is_pressed(self):
        # Start moving clockwise
        self._mock_motor.clockwise = True
        for i in range(10):
            self._axis.step()

        # Set-up limit switch to be triggered
        def press_switch_on_first_step_then_assert_anticlockwise():
            self._mock_limit_switches[0].is_pressed = True
            self._mock_motor.step.side_effect = lambda: self.assertFalse(self._mock_motor.clockwise,
                                                                         msg="Shouldn't be stepping clockwise!")

        self._mock_motor.step.side_effect = press_switch_on_first_step_then_assert_anticlockwise

        # Test that we do not step further
        try:
            for i in range(10):
                self._axis.step()
        except UnexpectedLimitSwitchError:
            # We expect this error!
            pass

    def test_current_location_shows_2mm_backoff_after_a_limit_switch_is_pressed(self):
        """Only 2mm since then if we go the wrong way, we have not gone through the whole travel of the switch."""

        # Step the axis for a bit
        for i in range(10):
            self._axis.step()

        # Then trigger a limit switch press
        collision_location = self._axis.current_location
        if self._axis.forwards:
            expected_backoff_location = collision_location - 2
        else:
            expected_backoff_location = collision_location + 2

        self._trigger_limit_switch_on_next_step()

        try:
            self._axis.step()
        except UnexpectedLimitSwitchError:
            pass

        # Verify that we backed off
        self.assertAlmostEqual(self._axis.current_location, expected_backoff_location,
                               delta=self._axis.millimetres_per_step)

    def test_raises_even_when_overridden_if_switch_is_still_pressed_after_backoff(self):
        self._trigger_limit_switch_on_next_step()
        self._axis.override_limit_switches = True
        with self.assertRaises(UnexpectedLimitSwitchError):
            self._axis.step()

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._trigger_limit_switch_on_next_step(switch_index=i)

            with self.assertRaises(UnexpectedLimitSwitchError):
                self._axis.step()

    def _trigger_limit_switch_on_next_step(self, switch_index=0):
        def press_limit_switch():
            self._mock_limit_switches[switch_index].is_pressed = True

        self._mock_motor.step.side_effect = press_limit_switch

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


class AxisHomingTest(BaseTestCases.Axis):
    """Tests the behaviour of the Axis.home() method."""

    def setUp(self):
        super().setUp()
        self.true_motor_location_in_steps = 20  # Some non-zero start location
        self._mock_motor.step.side_effect = self._default_motor_side_effect

    def _default_motor_side_effect(self):
        # Advance the 'real' location (in steps)
        if self._mock_motor.clockwise:
            self.true_motor_location_in_steps += 1
        else:
            self.true_motor_location_in_steps -= 1

        # Check for limit switch press
        if 0 < self.true_motor_location_in_steps < 200:
            self._mock_limit_switches[0].is_pressed = False
        else:
            self._mock_limit_switches[0].is_pressed = True

    def test_doesnt_advance_past_limit_switch(self):
        def new_motor_side_effect():
            self._default_motor_side_effect()
            self.assertTrue(0 <= self.true_motor_location_in_steps <= 200)

        self._mock_motor.step.side_effect = new_motor_side_effect
        self._axis.home()

    def test_ends_2mm_behind_secondary_limit_switch(self):
        self._axis.home()
        steps_in_2mm = 2 / self._axis.millimetres_per_step
        self.assertEqual(self.true_motor_location_in_steps, 200 - steps_in_2mm)

    def test_current_location_would_be_home_location_at_limit_switch(self):
        self._axis.home()
        true_motor_location_mm = self.true_motor_location_in_steps * self._axis.millimetres_per_step
        self.assertAlmostEqual(self._axis.current_location, true_motor_location_mm,
                               delta=self._axis.millimetres_per_step / 2)

    def test_is_homed_property_is_initially_false(self):
        self.assertFalse(self._axis.is_homed)

    def test_is_homed_property_is_true_after_home(self):
        self._axis.home()
        self.assertTrue(self._axis.is_homed)

    def test_returns_secondary_limit_switch_location(self):
        self._axis.home()
        self.assertAlmostEqual(self._axis.secondary_home_position.location,
                               200 * self._axis.millimetres_per_step,
                               delta=self._axis.millimetres_per_step/2)


class AxisPairHomingTest(unittest.TestCase):
    def setUp(self):
        self._mock_x_axis = MagicMock(name='x_axis', spec_set=stepper_control.Axis, is_homed=False,
                                      home_position=roboplot.core.home_position.HomePosition())
        self._mock_y_axis = MagicMock(name='y_axis', spec_set=stepper_control.Axis, is_homed=False,
                                      home_position=roboplot.core.home_position.HomePosition())
        self._both_axes = stepper_control.AxisPair(y_axis=self._mock_y_axis, x_axis=self._mock_x_axis)

        def home_x():
            self._mock_x_axis.is_homed = True
            return 210

        self._mock_x_axis.home.side_effect = home_x

        def home_y():
            self._mock_y_axis.is_homed = True
            return 279

        self._mock_y_axis.home.side_effect = home_y

    def test_both_axes_homed(self):
        self._both_axes.home()
        self.assertTrue(self._mock_x_axis.home.called)
        self.assertTrue(self._mock_y_axis.home.called)

    def test_is_homed_property_is_initially_false(self):
        self.assertFalse(self._both_axes.is_homed)

    def test_is_homed_property_is_true_after_home(self):
        self._both_axes.home()
        self.assertTrue(self._both_axes.is_homed)


if __name__ == '__main__':
    unittest.main()
