"""
This module defines a class to manage encoder activities.

Author: Luke W
"""

import threading
import warnings

from roboplot.core.gpio.gpio_wrapper import GPIO


class AxisEncoder(threading.Thread):
    """This class is a collection of functions and variables to setup and use an encoder"""

    _lock = threading.Lock()
    _count = 0
    _exit_requested = False

    def __init__(self, pins, positions_per_revolution, thread_name=None):
        """
        Initialises the encoder class.

        Args:
            pins: BCM number of the GPIO pins which make up the A and B channel of the encoder.
                  See pin allocation scheme on google drive.

            positions_per_revolution (int): the number of counts the encoder has per revolution.

            thread_name (str): a name to use to identify the base class thread object.
        """

        # Initialise thread object (base class initialiser)
        threading.Thread.__init__(self, group=None, target=self.encoder_loop, name=thread_name)

        # In python, class members appear to be created when you refer to them
        self._positions_per_revolution = positions_per_revolution
        self._a_pin = pins[0]
        self._b_pin = pins[1]

        # Setup pins
        for pin in (self._a_pin, self._b_pin):
            GPIO.setup(pin, GPIO.IN)

    @property
    def revolutions(self):
        """The number of partial revolutions completed since the last reset (or since initialisation)."""
        return self._count / self._positions_per_revolution

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

    def encoder_loop(self):
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
            count_change = _get_modular_representative(current_section - previous_section)

            # But if it is not...
            if count_change == 2:
                warnings.warn("Encoder moved more than one step")
                count_change = 0  # We do not know whether we gained two or lost two steps - so do nothing!

            # Use a lock to make count variable thread safe
            if count_change != 0:
                with self._lock:
                    self._count += count_change


def _get_modular_representative(value, min, modulus):
    return ((value - min) % modulus) + min
