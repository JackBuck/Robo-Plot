"""
This module defines all GPIO motor connections.

Authors:
    Hannah Howell, Jack Buckingham
"""

import time
import math
from Geometry import CalcLineDistances
# import RPi.GPIO as GPIO
from EmulatorGUI import GPIO


class StepperMotor:
    """This class is the collection of functions to set up and use a stepper motor."""

    def __init__(self, pins, sequence, steps_per_revolution):
        """
        Initialises the Motor class.

        Args:
            pins: The GPIO pins to which the real motor is connected.

            sequence: The step _sequence associated with the stepper motor. This should be a (python) _sequence of four
                      sequences of length four. The ith element gives the states of the four pins at the ith step.

            steps_per_revolution: The number of steps required to turn the motor one revolution.
        """

        self.clockwise = True
        self._next_step = 0

        self._gpio_pins = pins
        self._sequence = sequence
        self._steps_per_revolution = steps_per_revolution

        if not GPIO.setModeDone:  # TODO: I am not sure whether this is part of the RPi.GPIO module or not!
            GPIO.setmode(GPIO.BCM)

        # Setup pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def step(self):
        """This function steps the motor once and increments the _sequence."""

        for pin in range(0, 4):  # Creates an Index from 0-3

            # Check what status the current pin should be set to based on the current step count.
            current_pin = self._gpio_pins[pin]

            if self._sequence[self._next_step][pin] == 1:
                # Keep/Turn on the pin
                GPIO.output(current_pin, True)
            else:
                # Keep/Turn off the pin off
                GPIO.output(current_pin, False)

        # Increment / decrement the step count based on the direction of the motor.
        if self.clockwise:
            self._next_step = (self._next_step + 1) % 4
        else:
            self._next_step = (self._next_step - 1) % 4

    def start(self, duration, rps):
        """
        This function starts the motor running at the stored rps and direction of the motor for the specified amount
        of time (in seconds).

        Args:
            duration (float): The total time in seconds for which the motor should run.
            rps (float): The speed of the motor in revolutions per second.

        Returns:
            None

        """

        number_of_steps = round(rps * self._steps_per_revolution * duration)
        wait_time = 1 / (rps * self._steps_per_revolution)

        for step in range(number_of_steps):
            self.step()
            time.sleep(wait_time)


    def start_distance(self, distance, Vmax, Amax, DecMax):
        """
        This function starts the motor running at the stored rps and direction of the motor for the specified amount
        of time (in seconds).

        Args:
            duration (float): The total time in seconds for which the motor should run.
            rps (float): The speed of the motor in revolutions per second.

        Returns:
            None

        """

        D = CalcLineDistances(Vmax,Amax, DecMax, distance)

        for step in range(0, int(D[0])):
            self.step()

            current_velocity_time = math.sqrt(2*step*D[3])

            if current_velocity_time < 1:
                current_velocity_time = 1

            time.sleep(1/current_velocity_time)

        for step in range(int(D[0]), int(D[1])):
            self.step()
            current_velocity_time = 1/D[2]
            time.sleep(1/current_velocity_time)

        for step in range(int(D[1]), distance):
            self.step()
            current_velocity_time = math.sqrt(2*D[4]*(step-D[1]+(D[2]**2)/(2*D[4])))
            time.sleep(1/current_velocity_time)

    def change_direction(self, clockwise):
        """This function changes the direction the motor will move in the next time it steps.
           This function is simple and is not currently tested."""
        self.clockwise = clockwise

    def __str__(self):
        buf = "Motors.py: Pins:" + str(self.pins[0]) + str(self.pins[2]) + str(self.pins[3]) + str(self.pins[4])
        return buf


def large_stepper_motor(gpio_pins):
    """
    Creates a StepperMotor with the step _sequence and number of steps per revolution of the large stepper motor
    (42BYGHW208).

    Args:
        gpio_pins: The gpio pins to which the motor is connected.

    Returns:
        StepperMotor: An API for the stepper motor.

    """
    return StepperMotor(gpio_pins,
                        sequence=[[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]],
                        steps_per_revolution=200)


def small_stepper_motor(gpio_pins):
    """
    Creates a StepperMotor with the step _sequence and number of steps per revolution of the small stepper motor
    (28BYJ-48).

    Args:
        gpio_pins: The gpio pins to which the motor is connected.

    Returns:
        StepperMotor: An API for the stepper motor.

    """
    return StepperMotor(gpio_pins,
                        sequence=[[0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1], [1, 1, 0, 0]],
                        steps_per_revolution=4096)
