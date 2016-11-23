import unittest
from unittest.mock import call, create_autospec

import Motors
import StepperControl


class TestStepperMotorPair(unittest.TestCase):
    def setUp(self):
        # Create our mocks - autospeccing with set_spec they should throw is we try to access methods / attributes
        # and set attributes not on the Motors.StepperMotor class.

        # Annoyingly, it seems I must specify steps_per_revolution manually, since else when they are accessed they
        # are created as mocks in their own right and, in particular, do not show up as equal!

        # NB it is important for the autospeccing that all 'public' attributes of the StepperMotor class are defined
        # in the class body and not implicitly inside the __init__ method
        self.first_motor = create_autospec(Motors.StepperMotor, spec_set=True, _name='first_motor',
                                           steps_per_revolution=200)
        self.second_motor = create_autospec(Motors.StepperMotor, spec_set=True, _name='second_motor',
                                            steps_per_revolution=200)

    def test_throws_when_creating_motors_with_different_numbers_of_steps_per_revolution(self):
        self.second_motor.steps_per_revolution = self.first_motor.steps_per_revolution + 100

        with self.assertRaises(NotImplementedError):
            StepperControl.StepperMotorPair(self.first_motor, self.second_motor)

    def test_step_by_steps_motors_by_the_correct_numbers_of_steps(self):
        motor_pair = StepperControl.StepperMotorPair(self.first_motor, self.second_motor)
        motor_pair.step_by(first_motor_steps=200,
                           second_motor_steps=400,
                           sum_of_rps=10)

        self.first_motor.step.assert_has_calls([call()] * 200)
        self.second_motor.step.assert_has_calls([call()] * 400)


if __name__ == '__main__':
    unittest.main()
