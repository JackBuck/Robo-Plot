#!/usr/bin/env python3

import unittest

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO


# Each set of tests can be in their own class, but it must derive from unnit.TestCase
class MotorTest(unittest.TestCase):

    # Each test has its own function here. There are lots of different functions to use in tests
    def testPass(self):
        self.assertTrue(True)

    def test_x_axis_step_sequence(self):
        # Define and construct x axis motor
        sequence = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]

        # A hack, but this is the price we pay for writing tests which use the EmulatorGUI.py
        axis_motor = hardware.x_axis_motor
        axis_motor.clockwise = True
        input_pins = axis_motor._gpio_pins
        axis_motor.step()
        current_pin_statuses = [GPIO.input(pin) for pin in input_pins]
        offset = sequence.index(current_pin_statuses)

        # Check it works for 10 step cycles.
        for step in range(0, 10):

            # Check each pin is correct after each step.
            current_pin_statuses = [GPIO.input(pin) for pin in input_pins]
            expected_pin_statuses = sequence[(step + offset) % 4]
            self.assertSequenceEqual(expected_pin_statuses, current_pin_statuses)

            axis_motor.step()


# Running this runs all the tests and outputs their results.
def main():
    unittest.main()


if __name__ == '__main__':
    main()
