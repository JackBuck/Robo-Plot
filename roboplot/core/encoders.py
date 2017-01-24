"""
This module defines a class to manage encoder activities.

Author: Luke W
"""

import threading

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

    def encoder_loop(self):

        a = GPIO.input(self._a_pin)
        b = GPIO.input(self._b_pin)

        # Infinite while loop until program ends, at which point a flag can be set from another thread
        while not self._exit_requested:

            # Get encoder pin values
            a_prev = a
            b_prev = b
            a = GPIO.input(self._a_pin)
            b = GPIO.input(self._b_pin)

            # Depending on what changes have occurred, increment or decrement the encoder value
            # Check current and previous values of encoders
            count_change = 0
            if (a == 0) and (a_prev == 0):
                if (b == 1) and (b_prev == 0):
                    count_change += 1
                if (b == 0) and (b_prev == 1):
                    count_change -= 1
            elif (a == 1) and (a_prev == 1):
                if (b == 1) and (b_prev == 0):
                    count_change -= 1
                if (b == 0) and (b_prev == 1):
                    count_change += 1

            if (b == 0) and (b_prev == 0):
                if (a == 1) and (a_prev == 0):
                    count_change -= 1
                if (a == 0) and (a_prev == 1):
                    count_change += 1
            elif (b == 1) and (b_prev == 1):
                if (a == 1) and (a_prev == 0):
                    count_change += 1
                if (a == 0) and (a_prev == 1):
                    count_change -= 1

            # Use a lock to make count variable thread safe
            with self._lock:
                self._count += count_change
