"""
This module defines the class(es) interfacing the limit switches.
"""


class LimitSwitch:
    @property
    def is_pressed(self):
        raise NotImplementedError()


class UnexpectedLimitSwitchError(Exception):
    """Notifies of an unexpected limit switch press."""

    def __init__(self, message='An unexpected limit switch press detected!'):
        Exception.__init__(self)
        self.message = message
