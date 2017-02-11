"""
This module defines the class(es) interfacing the limit switches.
"""


class LimitSwitch:
    def __init__(self):
        raise NotImplementedError()

    @property
    def is_pressed(self):
        raise NotImplementedError()


class UnexpectedLimitSwitchError(Exception):
    """
    Notifies of an unexpected limit switch press.

    Do NOT catch this exception -- instead use the Axis.override_limit_switches attribute to avoid raising it.
    """

    def __init__(self, message='An unexpected limit switch press detected!'):
        Exception.__init__(self)
        self.message = message
