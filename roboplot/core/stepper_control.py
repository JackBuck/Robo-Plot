"""
Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time

import numpy as np

import roboplot.core.debug_movement as debug_movement
from roboplot.core.stepper_motors import StepperMotor
from roboplot.core.curves import Curve
from roboplot.core.encoders import Encoder


class Axis:
    def __init__(self,
                 motor: StepperMotor,
                 encoder: Encoder,
                 lead: float,
                 invert_axis: bool = False):
        """
        Creates an Axis.

        By default, the 'forwards' direction is that induced by rotating the stepper motor clockwise. The axis can be
        inverted to change this behaviour.

        Args:
            motor (StepperMotor): The stepper motor driving the axis.
            encoder (Encoder): The encoder monitoring the axis position. The encoder should be inverted if
                                   necessary to align increasing revolutions with the clockwise motion of the stepper
                                   motor.
            lead (float): The lead of the axis, in millimetres per revolution of the motor. This should be positive!
            invert_axis (bool): Use this parameter to invert the position and direction reported by the axis.
        """
        assert lead > 0, "The lead specified must be positive!"
        assert isinstance(invert_axis, bool)

        self._motor = motor
        self._encoder = encoder
        self._lead = lead
        self._invert_axis = invert_axis
        self._position_offset = 0

    @property
    def current_location(self):
        """
        The current location as measured by the encoder.

        Set this property when homing the axis.

        Returns:
            the current position of the axis.
        """
        sign = -1 if self._invert_axis else 1
        return sign * (self._encoder.revolutions * self._lead + self._position_offset)

    @current_location.setter
    def current_location(self, value):
        sign = -1 if self._invert_axis else 1
        self._position_offset = sign * value
        self._encoder.reset_position()
        self._motor.cumulative_step_count = 0

    @property
    def expected_location(self):
        """
        The current location as estimated by the stepper motor.

        This property is reset when the current_location is reset.

        Returns:
            the current expected position of the axis.
        """
        sign = -1 if self._invert_axis else 1
        return sign * (self._motor.cumulative_step_count * self.millimetres_per_step + self._position_offset)

    @property
    def millimetres_per_encoder_mark(self) -> float:
        """The resolution of the current_location property."""
        return self._encoder.resolution * self._lead

    @property
    def millimetres_per_step(self) -> float:
        """The approximate length of a single step of the motor."""
        return self._lead / self._motor.steps_per_revolution

    @property
    def forwards(self) -> bool:
        """
        If true, then stepping the motor will move the axis 'forwards'.

        Returns:
            bool: true if stepping the motor moves the axis 'forwards'.
        """
        return self._motor.clockwise != self._invert_axis

    @forwards.setter
    def forwards(self, value: bool) -> None:
        self._motor.clockwise = value != self._invert_axis

    def step(self):
        """Move the axis the minimum possible amount in the current direction."""
        self._motor.step()

    def nearest_measureable_location(self, target_location):
        """
        Returns approximately the location of the nearest mark on the encoders.

        Args:
            target_location: the target location.

        Returns:
            approximately the nearest location to the target location which is measureable by the encoders.
        """
        current_location = self.current_location  # Cached in case the encoder changes during the method

        target_displacement = target_location - current_location
        best_measureable_location = \
            self.millimetres_per_encoder_mark * round(target_displacement / self.millimetres_per_encoder_mark)
        return best_measureable_location + current_location


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
        points = curve.to_series_of_points(resolution)
        distances_between_points = np.linalg.norm(points[1:] - points[0:-1], axis=1)
        cumulative_distances = np.cumsum(distances_between_points)
        target_times = time.time() + cumulative_distances / pen_speed

        self.current_location = points[0]  # Temporary until we can lift up the pen
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

        target_location = self._nearest_measureable_location(target_location)
        self._set_axis_directions_for(target_location)

        # TODO: This would be cleaner if I could think of a way to pull a class out with member variables
        # start_location, target_location, current_distances, ... Some sort of LinearMoveProgressTracker
        # Then you could refactor the following to read:
        #   while not axes_have_reached(target_location):
        #       self._step_the_axis_which_is_behind(target_location, start_location)
        #       time_of_next_step = ??
        #       _sleep_until(time_of_next_step)
        start_location = self.current_location
        target_distances = abs(target_location - start_location)
        current_distances = np.array([0, 0])

        # Checking at half the encoder resolution to avoid precision errors
        while any(current_distances < target_distances - self._millimetres_per_encoder_mark / 2):
            self._step_the_axis_which_is_behind(current_distances, target_distances)

            current_distances = abs(self.current_location - start_location)
            time_of_next_step = start_time + total_seconds * sum(current_distances) / sum(target_distances)
            _sleep_until(time_of_next_step)

    def _nearest_measureable_location(self, target_location):
        return (self.y_axis.nearest_measureable_location(target_location[0]),
                self.x_axis.nearest_measureable_location(target_location[1]))

    @property
    def _millimetres_per_encoder_mark(self):
        return np.array(self.y_axis.millimetres_per_encoder_mark,
                        self.x_axis.millimetres_per_encoder_mark)

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
