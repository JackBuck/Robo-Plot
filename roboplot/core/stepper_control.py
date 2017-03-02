"""
Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import warnings

import numpy as np

import roboplot.core.debug_movement as debug_movement
import roboplot.core.limit_switches as limit_switches
from roboplot.core.stepper_motors import StepperMotor
from roboplot.core.curves import Curve


class HomePosition:
    forwards = False
    location = 0

    def __init__(self, forwards=forwards, location=location):
        self.forwards = forwards
        self.location = location


class Axis:
    current_location = 0
    _is_homed = False

    # Small enough that if we back off in the wrong direction, we don't go through the whole travel of the switch.
    __back_off_millimetres = 2

    def __init__(self,
                 motor: StepperMotor,
                 lead: float,
                 limit_switch_pair,
                 home_position: HomePosition = HomePosition(),
                 invert_axis: bool = False):
        """
        Creates an Axis.

        Args:
            motor (stepper_motors.StepperMotor): The stepper motor driving the axis.
            lead (float): The lead of the axis, in millimetres per revolution of the motor.
            limit_switch_pair (iterable of LimitSwitch): The pair of limit switches at each end of the axis.
            invert_axis (bool): Use this parameter to invert the position and direction reported by the axis.
        """
        assert lead > 0, "The lead specified must be positive!"
        assert isinstance(invert_axis, bool)

        self._motor = motor
        self._lead = lead
        self._limit_switches = limit_switch_pair
        self._home_position = home_position
        self._invert_axis = invert_axis

    @property
    def back_off_millimetres(self):
        return self.__back_off_millimetres

    @property
    def millimetres_per_step(self):
        return self._lead / self._motor.steps_per_revolution

    @property
    def forwards(self) -> bool:
        return self._motor.clockwise != self._invert_axis

    @forwards.setter
    def forwards(self, value: bool) -> None:
        self._motor.clockwise = value != self._invert_axis

    @property
    def is_homed(self):
        return self._is_homed

    def home(self) -> None:
        """
        Home the axis by driving into the limit switch and setting the current_location upon reaching it.

        The home_position argument to Axis.__init__ controls the direction in which to home as well as the value set
        upon reaching it.
        """
        self.forwards = self._home_position.forwards

        # Check that a limit switch is not currently pressed
        if any([switch.is_pressed for switch in self._limit_switches]):
            raise limit_switches.UnexpectedLimitSwitchError("Cannot home if switch is already pressed!")

        # Step until a switch is hit
        hit_location = self._step_expecting_limit_switch()
        while hit_location is None:
            hit_location = self._step_expecting_limit_switch()

        # Set the current location to the home position at the point where the limit switch is hit
        # Note that we back-calculate to account for any backoff.
        distance_moved_since_switch_pressed = self.current_location - hit_location
        self.current_location = self._home_position.location + distance_moved_since_switch_pressed

        self._is_homed = True

    def _step_expecting_limit_switch(self):
        """
        Step if there is no current limit switch press.
        Instead of raising on a switch press, back off and return the location of the collision.

        Returns:
            The current_location when the switch press occurred.
        """
        a_switch_is_pressed = any(switch.is_pressed for switch in self._limit_switches)
        if not a_switch_is_pressed:
            self._step_unsafe()
            a_switch_is_pressed = any(switch.is_pressed for switch in self._limit_switches)

        if a_switch_is_pressed:
            hit_location = self.current_location
            self._back_off()  # Force a back off for safety
            return hit_location  # Allow the caller the make use of the hit location, e.g. for homing

    def step(self) -> None:
        a_switch_is_pressed = any(switch.is_pressed for switch in self._limit_switches)
        if not a_switch_is_pressed:
            self._step_unsafe()
            a_switch_is_pressed = any(switch.is_pressed for switch in self._limit_switches)

        if a_switch_is_pressed:
            self._back_off()
            raise limit_switches.UnexpectedLimitSwitchError(
                message='Cannot step motor when limit switch is pressed!')

    def _back_off(self):
        """
        Reverse by the configured backoff distance.
        """
        originally_forwards = self.forwards
        try:
            self.forwards = not self.forwards
            # TODO: When you introduce the encoders, be sure to use the stepper motor internal value here,
            # at least if possible - since else if the encoder breaks for some reason you will not stop backing off
            # and risk crashing.
            initial_location = self.current_location
            while abs(initial_location - self.current_location) < abs(self.back_off_millimetres):
                self._step_unsafe()
        finally:
            self.forwards = originally_forwards

        if any(switch.is_pressed for switch in self._limit_switches):
            raise limit_switches.UnexpectedLimitSwitchError(message='Limit switch is still pressed after backoff!')

    def _step_unsafe(self):
        """Step without paying attention to the limit switches."""
        self._motor.step()
        self._advance_current_location()

    def _advance_current_location(self):
        if self.forwards:
            self.current_location += self.millimetres_per_step
        else:
            self.current_location -= self.millimetres_per_step

    def nearest_reachable_location(self, target_location):
        target_displacement = target_location - self.current_location
        best_possible_displacement = self.millimetres_per_step * round(target_displacement / self.millimetres_per_step)
        return best_possible_displacement + self.current_location


class AxisPair:
    def __init__(self, y_axis: Axis, x_axis: Axis):
        self.x_axis = x_axis
        self.y_axis = y_axis

    @property
    def current_location(self):
        return np.array([self.y_axis.current_location, self.x_axis.current_location])

    @current_location.setter
    def current_location(self, value):
        self.y_axis.current_location = value[0]
        self.x_axis.current_location = value[1]

    def home(self):
        self.x_axis.home()
        self.y_axis.home()

    @property
    def is_homed(self):
        return self.x_axis.is_homed and self.y_axis.is_homed

    def follow(self, curve: Curve, pen_speed: float, resolution: float = 0.1) -> None:
        """
        Step the motors so as to follow a curve.

        Args:
            curve (Curve): The curve to follow.
            pen_speed (float): The target speed of the pen (in MILLIMETRES / SECOND).
            resolution (float): The resolution to use when splitting the curve into line segments (in MILLIMETRES).

        Returns:
            None

        """
        if not self.is_homed:
            warnings.warn("Attempting to follow curve without having been homed!!")

        points = curve.to_series_of_points(resolution)
        distances_between_points = np.linalg.norm(points[1:] - points[0:-1], axis=1)
        cumulative_distances = np.cumsum(distances_between_points)
        target_times = time.time() + cumulative_distances / pen_speed

        for pt, target_time in zip(points[1:], target_times):
            self.move_linearly(pt, target_time)

    def move_linearly(self, target_location: np.ndarray, target_completion_time: float) -> None:
        """
        Steps the motors as close to linearly as possible to achieve the specified axis positions.

        Args:
            target_location (float): An 2-element array whose first (resp. second) elements determine the position to
                                     which to move the first (resp. second) axis. (in MILLIMETRES)
            target_completion_time (float): The target time at which the move should be completed. This should be
                                            given as a number of seconds since the Epoch (the same format as returned by
                                            time.time()).
                                            If this is in the past then the move will be conducted as fast as possible.
        """
        start_time = time.time()
        total_seconds = target_completion_time - start_time

        target_location = self._nearest_reachable_location(target_location)
        self._set_axis_directions_for(target_location)

        # TODO: This would be cleaner if I could think of a way to pull a class out with member variables
        # start_location, target_location, current_distances, ... Some sort of LinearMoveProgressTracker
        start_location = self.current_location
        target_distances = abs(target_location - start_location)
        current_distances = np.array([0, 0])

        while any(current_distances < target_distances):
            self._step_the_axis_which_is_behind(current_distances, target_distances)

            current_distances = abs(self.current_location - start_location)
            time_of_next_step = start_time + total_seconds * sum(current_distances) / sum(target_distances)
            _sleep_until(time_of_next_step)

    def _nearest_reachable_location(self, target_location):
        return (self.y_axis.nearest_reachable_location(target_location[0]),
                self.x_axis.nearest_reachable_location(target_location[1]))

    def _set_axis_directions_for(self, target_location):
        self.y_axis.forwards = target_location[0] >= self.current_location[0]
        self.x_axis.forwards = target_location[1] >= self.current_location[1]

    def _step_the_axis_which_is_behind(self, current_distances, target_distances):
        if current_distances[0] >= target_distances[0]:
            self.x_axis.step()
        elif current_distances[0] * target_distances[1] <= current_distances[1] * target_distances[0]:
            self.y_axis.step()
        else:
            self.x_axis.step()


class AxisPairWithDebugImage(AxisPair):
    @staticmethod
    def create_from(axes: AxisPair):
        return AxisPairWithDebugImage(y_axis=axes.y_axis, x_axis=axes.x_axis)

    def __init__(self, y_axis: Axis, x_axis: Axis):
        super().__init__(y_axis, x_axis)
        self.debug_image = debug_movement.DebugImage(self.x_axis.millimetres_per_step)

    @property
    def current_location(self):
        return super().current_location

    @current_location.setter
    def current_location(self, value):
        AxisPair.current_location.__set__(self, value)
        self.debug_image.add_point(value)
        self.debug_image.change_colour()

    def follow(self, curve: Curve, pen_speed: float, resolution: float = 0.1):
        self.debug_image.change_colour()
        super().follow(curve, pen_speed, resolution)
        self.debug_image.save_image()

    def _step_the_axis_which_is_behind(self, current_distances, target_distances):
        super()._step_the_axis_which_is_behind(current_distances, target_distances)
        self.debug_image.add_point(self.current_location)


def _sleep_until(wake_time):
    sleep_duration = wake_time - time.time()
    if sleep_duration > 0:
        time.sleep(sleep_duration)
