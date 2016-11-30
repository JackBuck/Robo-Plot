import time

import Motors


class StepperMotorPair:
    """Represents a synchronised pair of stepper motors."""

    def __init__(self, first_motor: Motors.StepperMotor, second_motor: Motors.StepperMotor):
        """
        Initialise a synchronised pair of stepper motors.

        Currently there is no implementation for synchronising motors with different step sizes.

        Args:
            first_motor: The first stepper motor
            second_motor: The second stepper motor
        """
        if first_motor.steps_per_revolution != second_motor.steps_per_revolution:
            raise NotImplementedError('There is currently no implementation for synchronising motors with different '
                                      'step sizes.')

        self._first_motor = first_motor
        self._second_motor = second_motor

    def step_by(self, first_motor_steps: int, second_motor_steps: int, sum_of_rps: float) -> None:
        """
        Steps the motors as close to linearly as possible by the specified amounts.

        Supply negative numbers of steps to achieve motion in the opposite direction.

        Args:
            first_motor_steps: The number of steps to advance the first motor.
            second_motor_steps: The number of steps to advance the second motor.
            sum_of_rps: The sum of the revolutions per second of the motors. While unnatural in an API, this is what
                        is easiest on the 'inside'. It will be changed once we know how we want to call this method.

        Returns:
            None

        """
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
