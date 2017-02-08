import unittest
from unittest.mock import MagicMock

import roboplot.core.stepper_control as stepper_control
import roboplot.core.limit_switches as limit_switches
import roboplot.core.stepper_motors as stepper_motors


class AxisTest(unittest.TestCase):

    def setUp(self):
        self._mock_limit_switches = (self._make_mock_switch(), self._make_mock_switch())
        self._mock_motor = MagicMock(spec=stepper_motors.StepperMotor)
        self._axis = stepper_control.Axis(self._mock_motor, 8, self._mock_limit_switches)

    @staticmethod
    def _make_mock_switch():
        mock = MagicMock(spec=limit_switches.LimitSwitch)
        assert hasattr(mock, 'is_pressed'), "Code has been refactored and test is out of date!"
        mock.is_pressed = False
        return mock

    def test_stepping_does_not_raise_when_no_limit_switch_is_pressed(self):
        self._axis.step()

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._mock_limit_switches[i].is_pressed = True

            with self.assertRaises(limit_switches.UnexpectedLimitSwitchError):
                self._axis.step()

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


if __name__ == '__main__':
    unittest.main()
