#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock

import context
import roboplot.core.stepper_control as stepper_control
from roboplot.core.limit_switches import LimitSwitch, UnexpectedLimitSwitchError
from roboplot.core.stepper_motors import StepperMotor
from roboplot.core.encoders import Encoder


def _add_side_effect(mock, *extra_effects):
    old_effect = mock.side_effect

    def new_side_effect():
        if old_effect is not None:
            old_effect()
        for effect in extra_effects:
            effect()

    mock.side_effect = new_side_effect


class OneTimeSideEffect:
    """
    A callable class which only does anything the first time it is called.

    It is intended to be used to add a side effect which only has an effect the first time the mock is called.
    """

    def __init__(self, effect):
        self._effect = effect
        self._has_been_called = False

    def __call__(self, *args, **kwargs):
        if not self._has_been_called:
            self._has_been_called = True
            self._effect()


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

            self._mock_encoder = MagicMock(name='encoder', spec_set=Encoder, resolution=1 / 200, revolutions=0)
            _add_side_effect(self._mock_encoder.reset_position, self._reset_encoder_count)

            self._mock_motor = MagicMock(name='motor', spec_set=StepperMotor, steps_per_revolution=200, clockwise=True,
                                         cumulative_step_count=0)
            self._add_to_motor_step_side_effect(self._increment_encoder_count, self._increment_motor_count)

            self._axis = stepper_control.Axis(motor=self._mock_motor,
                                              encoder=self._mock_encoder,
                                              lead=8,
                                              limit_switch_pair=self._mock_limit_switches)

        def _add_to_motor_step_side_effect(self, *extra_effects):
            _add_side_effect(self._mock_motor.step, *extra_effects)

        def _increment_encoder_count(self):
            if self._mock_motor.clockwise:
                self._mock_encoder.revolutions += self._mock_encoder.resolution
            else:
                self._mock_encoder.revolutions -= self._mock_encoder.resolution

        def _increment_motor_count(self):
            if self._mock_motor.clockwise:
                self._mock_motor.cumulative_step_count += 1
            else:
                self._mock_motor.cumulative_step_count -= 1

        def _reset_encoder_count(self):
            self._mock_encoder.revolutions = 0


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
        self._trigger_limit_switch_on_next_step()

        # Add a side effect to check that we have at most one future clockwise step
        # NB: the step which triggers the switch press is a clockwise step
        self._mock_motor.step.reset_mock()

        def assert_no_more_than_one_clockwise_step():
            if len(self._mock_motor.step.mock_calls) > 1:
                self.assertFalse(self._mock_motor.clockwise, msg="Shouldn't be stepping clockwise!")

        self._add_to_motor_step_side_effect(assert_no_more_than_one_clockwise_step)

        # Try stepping
        try:
            for i in range(10):
                self._axis.step()
        except UnexpectedLimitSwitchError:
            # We expect this error!
            pass

    def test_current_location_shows_2mm_backoff_according_to_stepper_after_a_limit_switch_is_pressed(self):
        """Only 2mm since then if we go the wrong way, we have not gone through the whole travel of the switch."""

        # Step the axis for a bit
        for i in range(10):
            self._axis.step()

        # Then trigger a limit switch press and compute where we expect to back off to
        self._mock_motor.step.reset_mock()
        self._trigger_limit_switch_on_next_step()

        try:
            self._axis.step()
        except UnexpectedLimitSwitchError:
            pass

        # Verify that we backed off the correct number of steps
        steps_in_2mm = 2 / self._axis.millimetres_per_step
        self.assertEqual(self._mock_motor.step.call_count,
                         steps_in_2mm+1)  # NB the first step is forwards since it's the one which triggers the switch!

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._trigger_limit_switch_on_next_step(switch_index=i)

            with self.assertRaises(UnexpectedLimitSwitchError):
                self._axis.step()

    def _trigger_limit_switch_on_next_step(self, switch_index=0):
        def press_limit_switch():
            self._mock_limit_switches[switch_index].is_pressed = True

        press_limit_switch_once = OneTimeSideEffect(press_limit_switch)
        self._add_to_motor_step_side_effect(press_limit_switch_once)

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


class AxisHomingTest(BaseTestCases.Axis):
    """Tests the behaviour of the Axis.home() method."""

    def setUp(self):
        super().setUp()
        self.true_motor_location_in_steps = 20  # Some non-zero start location
        self._add_to_motor_step_side_effect(self._increment_true_step_count, self._update_limit_switches)

    def _increment_true_step_count(self):
        if self._mock_motor.clockwise:
            self.true_motor_location_in_steps += 1
        else:
            self.true_motor_location_in_steps -= 1

    def _update_limit_switches(self):
        self._mock_limit_switches[0].is_pressed = self.true_motor_location_in_steps <= 0
        self._mock_limit_switches[1].is_pressed = self.true_motor_location_in_steps >= 200

    def test_doesnt_advance_past_limit_switch(self):
        self._add_to_motor_step_side_effect(lambda: self.assertTrue(0 <= self.true_motor_location_in_steps <= 200))
        self._axis.home()

    def test_ends_2mm_behind_limit_switch(self):
        self._axis.home()
        steps_in_2mm = 2 / self._axis.millimetres_per_step
        self.assertEqual(self.true_motor_location_in_steps, steps_in_2mm)

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


class AxisPairHomingTest(unittest.TestCase):
    def setUp(self):
        self._mock_x_axis = MagicMock(name='x_axis', spec_set=stepper_control.Axis, is_homed=False)
        self._mock_y_axis = MagicMock(name='x_axis', spec_set=stepper_control.Axis, is_homed=False)
        self._both_axes = stepper_control.AxisPair(y_axis=self._mock_y_axis, x_axis=self._mock_x_axis)

        def home_x():
            self._mock_x_axis.is_homed = True

        self._mock_x_axis.home.side_effect = home_x

        def home_y():
            self._mock_y_axis.is_homed = True

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
