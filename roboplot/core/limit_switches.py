"""
This module defines the class(es) interfacing the limit switches.
"""

import numpy as np

from roboplot.core.home_position import HomePosition
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


class PretendLimitSwitch:
    """
    A replacement class to allow the scripts to run without hardware.

    Note that this class uses the Axis.current_location property, so if a limit switch with a valid range of 0 is
    used to home at 0, then a drift in the real position will be observed on repeated homes. Similarly for any other
    value for the home position.
    """
    _parent_axis = None
    _valid_range = None

    def __init__(self, valid_range):
        """
        Create a pretend limit switch, which triggers when outside a specified valid range.

        Note that the class must still be registered to a parent axis before it can be used!

        Args:
            valid_range (tuple): an ordered pair of numbers, one of which is infinite, which define the range in which
                                 the limit switch will return False to is_pressed.
        """
        assert len(valid_range) == 2
        assert sum(np.isinf(valid_range)) == 1
        assert valid_range[0] < valid_range[1]

        self._valid_range = valid_range

    def register_parent_axis(self, parent_axis) -> None:
        """
        Register the parent axis of this limit switch.

        Args:
            parent_axis (stepper_control.Axis): the parent axis whose current_location will be used
        """
        self._parent_axis = parent_axis

    @LimitSwitch.is_pressed.getter
    def is_pressed(self):
        return not self._valid_range[0] < self._parent_axis.current_location < self._valid_range[1]

    def get_location_infront_of_switch(self, millimetres):
        """Compute a location on the non-pressed side of the switch."""
        if np.isinf(self._valid_range[1]):
            return self._valid_range[0] + millimetres
        else:
            return self._valid_range[1] - millimetres


def define_pretend_limit_switches(home_position: HomePosition, separation: float) -> tuple:
    """A factory method for defining a pair of limit switches.

    Args:
        home_position (HomePosition): the homing configuration for the axis
        separation (float): the (positive) distance between the limit switches

    Returns:
        tuple: a pair of PretendLimitSwitch objects
    """

    assert separation > 0

    if home_position.forwards:
        switch_locations = home_position.location + np.array([-separation, 0])
    else:
        switch_locations = home_position.location + np.array([0, separation])

    return (PretendLimitSwitch(valid_range=(switch_locations[0], np.inf)),
            PretendLimitSwitch(valid_range=(-np.inf, switch_locations[1])))


class UnexpectedLimitSwitchError(Exception):
    """
    Notifies of an unexpected limit switch press.

    Do NOT catch this exception -- instead use the Axis.override_limit_switches attribute to avoid raising it.
    """

    def __init__(self, message='An unexpected limit switch press detected!'):
        Exception.__init__(self)
        self.message = message
