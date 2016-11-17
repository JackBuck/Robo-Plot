import time
import StepperControl
import Motors

def throws_when_creating_motors_with_different_numbers_of_steps_per_revolution():
    first = Motors.large_stepper_motor([17, 22, 23, 24])
    second = Motors.small_stepper_motor([7, 8, 9, 10])
    try:
        StepperControl.StepperMotorPair(first, second)
    except NotImplementedError:
        return

    raise AssertionError('No error thrown!!')


def run_step_by_with_test_inputs():
    """This is not a unit test but rather a method facilitating interactive testing of the class."""

    first_motor = Motors.large_stepper_motor([17, 22, 23, 24])
    second_motor = Motors.large_stepper_motor([7, 8, 9, 10])

    now = time.time()
    StepperControl.StepperMotorPair(first_motor, second_motor).step_by(200, 400, 100/200)
    print('Elapsed: {:.2f} seconds\n'.format(time.time() - now))

run_step_by_with_test_inputs()
