import time

import Motors


class StepperMotorPair:
    def __init__(self, first_motor: Motors.StepperMotor, second_motor: Motors.StepperMotor):
        if first_motor.steps_per_revolution != second_motor.steps_per_revolution:
            raise NotImplementedError('There is currently no implementation for synchronising motors with different '
                                      'step sizes.')

        self._first_motor = first_motor
        self._second_motor = second_motor

    def step_by(self, first_motor_steps, second_motor_steps, sum_of_rps):
        self._first_motor.clockwise = first_motor_steps >= 0
        first_motor_steps = abs(first_motor_steps)

        self._second_motor.clockwise = second_motor_steps >= 0
        second_motor_steps = abs(second_motor_steps)

        # We are restricting to the case where both motors have the same number of step per revolution
        seconds_per_step = 1 / (sum_of_rps * self._first_motor.steps_per_revolution)

        # TODO: Refactor this once we have encoders
        first_motor_step_count = 0
        second_motor_step_count = 0

        while True:
            if first_motor_step_count * second_motor_steps <= second_motor_step_count * first_motor_steps:
                self._first_motor.step()
                first_motor_step_count += 1
            else:
                self._second_motor.step()
                second_motor_step_count += 1

            if first_motor_step_count == first_motor_steps and second_motor_step_count == second_motor_steps:
                break

            time.sleep(seconds_per_step)
