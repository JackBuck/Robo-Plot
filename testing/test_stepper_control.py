import unittest
from unittest.mock import MagicMock

import roboplot.core.stepper_control as stepper_control
from roboplot.core.limit_switches import LimitSwitch, UnexpectedLimitSwitchError
from roboplot.core.stepper_motors import StepperMotor

import context
# noinspection PyUnresolvedReferences
import test_runner


class AxisTest(unittest.TestCase):
    def setUp(self):
        self._mock_limit_switches = (MagicMock(name='switch_1', spec_set=LimitSwitch, is_pressed=False),
                                     MagicMock(name='switch_2', spec_set=LimitSwitch, is_pressed=False))
        self._mock_motor = MagicMock(name='motor', spec_set=StepperMotor, steps_per_revolution=200, clockwise=True)
        self._axis = stepper_control.Axis(self._mock_motor, 8, self._mock_limit_switches)

    def test_stepping_does_not_raise_when_no_limit_switch_is_pressed(self):
        self._axis.step()

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._mock_limit_switches[i].is_pressed = True

            with self.assertRaises(UnexpectedLimitSwitchError):
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

    def test_current_location_shows_backoff_after_a_limit_switch_is_pressed(self):
        self._axis.back_off_millimetres = 5

        for i in range(10):
            self._axis.step()

        collision_location = self._axis.current_location
        if self._axis.forwards:
            expected_backoff_location = collision_location - 5
        else:
            expected_backoff_location = collision_location + 5
        self._mock_limit_switches[0].is_pressed = True

        try:
            self._axis.step()
        except UnexpectedLimitSwitchError:
            pass

        self.assertAlmostEqual(self._axis.current_location, expected_backoff_location,
                               delta=self._axis.millimetres_per_step)

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


if __name__ == '__main__':
    unittest.main(testRunner=test_runner.CustomTestRunner())
