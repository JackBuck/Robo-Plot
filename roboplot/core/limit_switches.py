"""
This module defines the class(es) interfacing the limit switches.
"""

from roboplot.core.gpio.gpio_wrapper import GPIO


class LimitSwitch:
    def __init__(self, gpio_pin):
        self._gpio_pin = gpio_pin
        GPIO.setup(self._gpio_pin, GPIO.IN)

    @property
    def is_pressed(self):
        if GPIO.input(self._gpio_pin) == 0:
            return True
        else:
            return False


class UnexpectedLimitSwitchError(Exception):
    """
    Notifies of an unexpected limit switch press.

    Do NOT catch this exception -- instead use the Axis.override_limit_switches attribute to avoid raising it.
    """

    def __init__(self, message='An unexpected limit switch press detected!'):
        Exception.__init__(self)
        self.message = message
