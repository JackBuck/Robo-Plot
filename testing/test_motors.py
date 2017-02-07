import context
import unittest
import cv2
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO
import time


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class MotorTest(unittest.TestCase):
    # Each test has its own function here. There are lots of different functions to use in tests
    def testPass(self):
        self.assertTrue(True)

    def testStepLarge(self):
        GPIO.cleanup()

        # Define and construct x axis motor
        input_pins = (22, 23, 24, 25)
        sequence = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]

        axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(input_pins))

        axis_motor.step()

        # Check it works for 10 step cycles.
        for step in range(0, 10):

            # Check each pin is correct after each step.
            for pin in range(0, 4):
                current_pin = input_pins[pin]
                pin_status = GPIO.input(current_pin)
                current_step = step % 4
                correct_status = (sequence[step % 4][pin] == 1)
                self.assertTrue(pin_status == correct_status)

            # Optional delay to visually see the changes.
            # time.sleep(1)

            axis_motor.step()


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
