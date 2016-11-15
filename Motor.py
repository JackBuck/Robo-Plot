# Author: Hannah Howell
# Date: 10/11/16

import time
# import RPi.GPIO as GPIO
from EmulatorGUI import GPIO


class Motor:
    """This class is the collection of functions to set up and use a motor."""

    def __init__(self, pins, sequence, steps_per_revolution):
        """
        Initialises the Motor class.

        Args:
            pins: The GPIO pins to which the real motor is connected.

            sequence: The step sequence associated with the stepper motor. This should be a (python) sequence of four
                      sequences of length four. The ith element gives the states of the four pins at the ith step.

            steps_per_revolution: The number of steps required to turn the motor one revolution.
        """

        self.GPIO_pins = pins
        self.sequence = sequence
        self.clockwise = True
        self.next_step = 0
        self.steps_per_revolution = steps_per_revolution

        # Setup pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def step(self):
        """This function steps the motor once and increments the sequence."""

        for pin in range(0, 4):  # Creates an Index from 0-3

            # Check what status the current pin should be set to based on the current step count.
            current_pin = self.GPIO_pins[pin]

            if self.sequence[self.next_step][pin] == 1:
                # Keep/Turn on the pin
                GPIO.output(current_pin, True)
            else:
                # Keep/Turn off the pin off
                GPIO.output(current_pin, False)

        # Increment / decrement the step count based on the direction of the motor.
        if self.clockwise:
            self.next_step = (self.next_step + 1) % 4
        else:
            self.next_step = (self.next_step - 1) % 4

    def start(self, duration, rps):
        """
        This function starts the motor running at the stored rps and direction of the motor for the specified amount
        of time (in seconds).

        Args:
            duration: The total time for which the motor should run.
            rps: The speed of the motor in revolutions per second.

        Returns:
            None

        """

        number_of_steps = duration / (rps * self.steps_per_revolution)

        # Step the motor the required number of steps. Waiting between the steps to achieve
        # required rps
        for step in range(0, number_of_steps):
            self.step()
            time.sleep(self.steps_per_revolution / rps)

    def change_direction(self, clockwise):
        """This function changes the direction the motor will move in the next time it steps.
        This function is simple and is not currently tested."""
        self.clockwise = clockwise

    def __str__(self):
        buf = "Motor.py: Pins:" + str(self.pins[0]) + str(self.pins[2]) + str(self.pins[3]) + str(self.pins[4])
        return buf
