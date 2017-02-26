"""
This module defines a class to manage encoder activities.

Author: Luke W (refactored by Jack)
"""

import threading
import warnings

from roboplot.core.gpio.gpio_wrapper import GPIO
from roboplot.core.stepper_motors import StepperMotor


class Encoder(threading.Thread):
    """This class is a collection of functions and variables to setup and use an encoder"""

    _lock = threading.Lock()
    _count = 0
    _exit_requested = False

    def __init__(self, gpio_pins, positions_per_revolution, clockwise_is_positive=False, thread_name=None):
        """
        Initialises the encoder class.

        Args:
            gpio_pins: BCM number of the GPIO pins which make up the A and B channel of the encoder.
                  See pin allocation scheme on google drive.

            positions_per_revolution (int): the number of counts the encoder has per revolution.

            clockwise_is_positive (bool): determines which direction is reported as 'increasing' revolutions.

            thread_name (str): a name to use to identify the base class thread object.
        """

        # Initialise thread object (base class initialiser)
        threading.Thread.__init__(self, group=None, target=self._encoder_loop, name=thread_name)

        # In python, class members appear to be created when you refer to them
        self._positions_per_revolution = positions_per_revolution
        self._clockwise_is_positive = clockwise_is_positive
        self._a_pin = gpio_pins[0]
        self._b_pin = gpio_pins[1]

        # Setup gpio_pins
        for pin in (self._a_pin, self._b_pin):
            GPIO.setup(pin, GPIO.IN)

    @property
    def resolution(self) -> float:
        """The size of a step on the encoder as a proportion of a revolution."""
        return 1 / self._positions_per_revolution

    @property
    def revolutions(self) -> float:
        """The number of partial revolutions completed since the last reset (or since initialisation)."""
        sign = 1 if self._clockwise_is_positive else -1  # TODO: Calibrate this against the real encoders...
        return sign * self._count / self._positions_per_revolution

    def reset_position(self):
        """
        This function resets the position to 0
        """
        with self._lock:
            self._count = 0

    def exit_thread(self):
        """
        This function sets up the conditions to kill the thread

        Shortly after calling this function the thread will exit
        """
        with self._lock:
            self._exit_requested = True  # TODO: Is there any point in locking here? We do not lock when we read it...

    def _encoder_loop(self):
        """
        Loop to update the encoder count until an exit is requested.

        Returns:
            None
        """

        current_section = self._compute_current_section()

        # Infinite while loop until program ends, at which point a flag can be set from another thread
        while not self._exit_requested:
            previous_section = current_section
            current_section = self._compute_current_section()

            # Sections are modulo 4; hopefully the change is 0,1, or -1 modulo 4
            count_change = _get_modular_representative(current_section - previous_section, min=-1, modulus=4)

            # But if it is not...
            if count_change == 2:
                warnings.warn("Encoder moved more than one step")
                count_change = 0  # We do not know whether we gained two or lost two steps - so do nothing!

            # Use a lock to make count variable thread safe
            if count_change != 0:
                with self._lock:
                    self._count += count_change

    def _compute_current_section(self):
        """
        Returns a number modulo 4 to indicate the current reading from the encoder.
        """
        a = GPIO.input(self._a_pin)
        b = GPIO.input(self._b_pin)

        return self._compute_section(a, b)

    @staticmethod
    def _compute_section(a, b):
        """
        Returns a number modulo 4 to indicate the state of the encoder corresponding to the supplied pin readings.

        Args:
            a: the pin reading for the A channel (either 0 or 1)
            b: the pin reading for the B channel (either 0 or 1)

        Returns:
            The value modulo 4 corresponding to the pin readings.
        """
        # return 3*a + (1-b)*(1-2*a)  # Some opaque magic...

        if (a, b) == (0, 1):
            return 0
        elif (a, b) == (0, 0):
            return 1
        elif (a, b) == (1, 0):
            return 2
        elif (a, b) == (1, 1):
            return 3
        else:
            assert False, "GPIO input pins returned unexpected values!"


def _get_modular_representative(value, min, modulus):
    return ((value - min) % modulus) + min


class PretendEncoder:
    """A wrapper class to give a StepperMotor an Encoder interface."""

    _offset_from_motor = 0

    def __init__(self, motor: StepperMotor):
        """
        Initialises an encoder which wraps a supplied encoder.

        Position measurements are determined by querying the supplied motor.

        This class is intended to be used as a replacement for a real encoder class when testing without real
        hardware. As such,the motor passed to this method is treated as completely 'readonly'.

        Args:
            motor: The stepper motor to wrap as an encoder.
        """
        self._motor = motor

    @property
    def resolution(self) -> float:
        """The size of a step on the encoder as a proportion of a revolution."""
        return 1 / self._motor.steps_per_revolution

    @property
    def revolutions(self):
        """The number of revolutions completed, as measured by the stepper motor."""
        return (self._motor.cumulative_step_count + self._offset_from_motor) / self._motor.steps_per_revolution

    def reset_position(self):
        """Resets the position of the encoder without affecting the count on the wrapped motor."""
        self._offset_from_motor = -self._motor.cumulative_step_count

    # noinspection PyMethodMayBeStatic
    def exit_thread(self):
        """Does nothing"""
        pass
