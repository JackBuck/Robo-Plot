import unittest
from unittest.mock import MagicMock

import roboplot.core.stepper_control as stepper_control
from roboplot.core.limit_switches import LimitSwitch, UnexpectedLimitSwitchError
from roboplot.core.stepper_motors import StepperMotor


class AxisTest(unittest.TestCase):

    def setUp(self):
        self._mock_limit_switches = (MagicMock(name='switch_1', spec_set=LimitSwitch, is_pressed=False),
                                     MagicMock(name='switch_2', spec_set=LimitSwitch, is_pressed=False))
        self._mock_motor = MagicMock(name='motor', spec_set=StepperMotor, steps_per_revolution=200)
        self._axis = stepper_control.Axis(self._mock_motor, 8, self._mock_limit_switches)

    def test_stepping_does_not_raise_when_no_limit_switch_is_pressed(self):
        self._axis.step()

    def test_stepping_raises_when_a_limit_switch_is_pressed(self):
        for i in 0, 1:
            self._reset_switches()
            self._mock_limit_switches[i].is_pressed = True

            with self.assertRaises(UnexpectedLimitSwitchError):
                self._axis.step()

    def _reset_switches(self):
        for switch in self._mock_limit_switches:
            switch.is_pressed = False


if __name__ == '__main__':
    unittest.main()
