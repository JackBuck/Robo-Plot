import unittest
from unittest.mock import MagicMock

import roboplot.core.stepper_control as stepper_control
from roboplot.core.limit_switches import LimitSwitch, UnexpectedLimitSwitchError
from roboplot.core.stepper_motors import StepperMotor

import context
# noinspection PyUnresolvedReferences
import test_runner


class BaseTestCases:
    """
    The test discovery system will (by default) only look inside module level classes deriving from unittest.TestCase.

    All test methods in base test classes will be run when their (module level) derived classes are tested.
    """
    class AxisLimitSwitch(unittest.TestCase):
        """Tests which hold both when the limit switches are overridden and when they are not."""

        def setUp(self):
            self._mock_limit_switches = (MagicMock(name='switch_1', spec_set=LimitSwitch, is_pressed=False),
                                         MagicMock(name='switch_2', spec_set=LimitSwitch, is_pressed=False))
            self._mock_motor = MagicMock(name='motor', spec_set=StepperMotor, steps_per_revolution=200, clockwise=True)
            self._axis = stepper_control.Axis(self._mock_motor, 8, self._mock_limit_switches)

        def test_stepping_does_not_raise_when_no_limit_switch_is_pressed(self):
            self._axis.step()

        def test_advances_no_further_when_a_limit_switch_is_pressed(self):
            # To be used later
            def assert_not_clockwise():
                self.assertFalse(self._mock_motor.clockwise,
                                 msg="Shouldn't be stepping clockwise!")

            # Start moving clockwise
            self._mock_motor.clockwise = True
            for i in range(10):
                self._axis.step()

            # Trigger a limit switch
            self._mock_limit_switches[0].is_pressed = True
            self._mock_motor.step.side_effect = assert_not_clockwise

            # Test that we do not step further
            try:
                for i in range(10):
                    self._axis.step()
            except UnexpectedLimitSwitchError:
                # We expect this error!
                pass

        def test_current_location_shows_2mm_backoff_after_a_limit_switch_is_pressed(self):
            """We test for a 2mm backoff since then if we go the wrong way, we have not gone through the whole travel of
            the switch."""
            def press_limit_switch():
                self._mock_limit_switches[0].is_pressed = True

            for i in range(10):
                self._axis.step()

            collision_location = self._axis.current_location
            if self._axis.forwards:
                expected_backoff_location = collision_location - 2
            else:
                expected_backoff_location = collision_location + 2

            self._mock_motor.step.side_effect = press_limit_switch

            try:
                self._axis.step()
            except UnexpectedLimitSwitchError:
                pass

            self.assertAlmostEqual(self._axis.current_location, expected_backoff_location,
                                   delta=self._axis.millimetres_per_step)

        def test_doesnt_backoff_if_switch_is_already_pressed(self):
            collision_location = self._axis.current_location
            self._mock_limit_switches[0].is_pressed = True
            try:
                self._axis.step()
            except UnexpectedLimitSwitchError:
                pass

            self.assertEqual(self._axis.current_location, collision_location)

        def test_raises_even_when_overridden_if_switch_is_still_pressed_after_backoff(self):
            def press_limit_switch():
                self._mock_limit_switches[0].is_pressed = True

            self._mock_motor.step.side_effect = press_limit_switch
            self._axis.override_limit_switches = True
            with self.assertRaises(UnexpectedLimitSwitchError):
                self._axis.step()


class AxisLimitSwitch(BaseTestCases.AxisLimitSwitch):
    def setUp(self):
        super().setUp()
        self._axis.override_limit_switches = False

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._mock_limit_switches[i].is_pressed = True

            with self.assertRaises(UnexpectedLimitSwitchError):
                self._axis.step()

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


class AxisLimitSwitchWithOverriddenSwitches(BaseTestCases.AxisLimitSwitch):
    def setUp(self):
        super().setUp()
        self._axis.override_limit_switches = True

    def test_overriding_limit_switches_prevents_raise(self):
        initial_location = self._axis.current_location

        def reset_switch_if_current_location_is_less_than_initial_location():
            if self._axis.current_location < initial_location:
                self._mock_limit_switches[0].is_pressed = False

        self._axis.forwards = True
        self._mock_motor.step.side_effect = reset_switch_if_current_location_is_less_than_initial_location

        self._mock_limit_switches[0].is_pressed = True
        self._axis.step()


if __name__ == '__main__':
    unittest.main(testRunner=test_runner.CustomTestRunner())
