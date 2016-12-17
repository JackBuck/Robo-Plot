"""Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time

import numpy as np

from roboplot import Motors


# TODO: Add functionality to chain curves
class Curve:
    @property
    def total_millimetres(self):
        """The total length of the curve (in MILLIMETRES)."""
        raise NotImplementedError("The total length property must be overriden in derived classes.")

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        """
        This method should be overridden in derived classes to return the coordinates on the curve at (a) given
        position(s).

        Args:
            arc_length (np.ndarray): A vector of positions along the curve, expressed in arc length in millimetres.

        Returns:
            np.ndarray: An nx2 matrix whose ith row is the ith requested point on the curve.

        """
        raise NotImplementedError("The parameterisation method must be overridden in derived classes.")

    def to_series_of_points(self, interval_millimetres: float, include_last_point: bool = True) -> np.ndarray:
        """Express the path by a series of points.

        Args:
            interval_millimetres (float): The size of each interval (in MILLIMETRES)
            include_last_point (bool): If true then the series of points will include the last point on the curve.
                                       Otherwise it will not, which is useful when chaining curves.

        Returns:
            np.ndarray: An nx2 matrix whose ith row is the ith point (in MILLIMETRES) to which to move the axes.

        """
        arc_lengths = np.arange(0, self.total_millimetres, interval_millimetres, dtype=float)

        if include_last_point:
            arc_lengths = np.append(arc_lengths, self.total_millimetres)

        return self.evaluate_at(arc_lengths)


class LineSegment(Curve):
    def __init__(self, start: np.ndarray, end: np.ndarray):
        """Define a line segment.

        Args:
            start (np.ndarray): The 2D start point (in MILLIMETRES).
            end (np.ndarray): The 2D end point (in MILLIMETRES).

        Returns:
            LineSegment: The line segment.

        """
        self.start = start.reshape(2)
        self.end = end.reshape(2)

    @property
    def total_millimetres(self) -> float:
        return np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = arc_length.reshape(-1, 1)  # Make it a column vector
        t = arc_length / self.total_millimetres
        return (1 - t) * self.start + t * self.end


class Circle(Curve):
    def __init__(self, centre: np.ndarray, radius: float):
        """
        Define a circle.

        Args:
            centre (np.ndarray): A 2-element vector specifying the centre of the circle (in MILLIMETRES).
            radius (float): The radius of the circle (in MILLIMETRES).
        """
        self.centre = np.reshape(centre, 2)
        self.radius = radius

    @property
    def total_millimetres(self):
        return 2 * np.pi * self.radius

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = arc_length.reshape(-1, 1)  # Make column vector
        radians = arc_length / self.radius
        points = np.hstack((np.cos(radians), np.sin(radians)))
        points = self.radius * points + self.centre
        return points


class Axis:
    current_location = 0

    def __init__(self, motor: Motors.StepperMotor, lead: float):
        """
        Creates an Axis.

        Args:
            motor (Motors.StepperMotor): The stepper motor driving the axis.
            lead (float): The lead of the axis, in millimetres per revolution of the motor.
        """
        self._motor = motor
        self._lead = lead

    @property
    def millimetres_per_step(self):
        return self._lead / self._motor.steps_per_revolution

    @property
    def forwards(self):
        return self._motor.clockwise

    @forwards.setter
    def forwards(self, value):
        self._motor.clockwise = value

    def _advance_current_location(self):
        if self.forwards:
            self.current_location += self.millimetres_per_step
        else:
            self.current_location -= self.millimetres_per_step

    def step(self):
        self._motor.step()
        self._advance_current_location()


class AxisPair:
    def __init__(self, x_axis: Axis, y_axis: Axis):
        self.x_axis = x_axis
        self.y_axis = y_axis

    @property
    def current_location(self):
        return np.array([self.x_axis.current_location, self.y_axis.current_location])

    @current_location.setter
    def current_location(self, value):
        self.x_axis.current_location = value[0]
        self.y_axis.current_location = value[1]

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
        self.current_location = points[0]  # Temporary until we can lift up the pen
        for pt in points[1:]:
            self.move_linearly(pt, pen_speed)

    def move_linearly(self, target_location: np.ndarray, pen_speed: float) -> None:
        """
        Steps the motors as close to linearly as possible to achieve the specified axis positions.

        Args:
            target_location (float): An 2-element array whose first (resp. second) elements determine the position to
                                     which to move the first (resp. second) axis. (in MILLIMETRES)
            pen_speed (float): The target speed of the pen (in MILLIMETRES / SECOND).

        """
        # TODO: Replace this first set of maths with a 'nearest reachable location' property on the Axis
        target_displacement = target_location - self.current_location
        millimetres_per_step = [self.x_axis.millimetres_per_step, self.y_axis.millimetres_per_step]
        xy_steps = np.round(target_displacement / millimetres_per_step)

        target_displacement = xy_steps * millimetres_per_step
        target_location = target_displacement + self.current_location

        # Address direction
        self.x_axis.forwards = target_location[0] >= self.current_location[0]
        self.y_axis.forwards = target_location[1] >= self.current_location[1]

        # Compute the wait time
        pen_millimetres = np.linalg.norm(target_displacement)
        total_seconds = pen_millimetres / pen_speed
        total_steps = sum(abs(xy_steps))
        seconds_per_step = total_seconds / total_steps

        # Step the motors
        start_location = self.current_location
        target_distances = abs(target_location - start_location)
        current_distances = abs(self.current_location - start_location)

        while any(current_distances < target_distances):
            if current_distances[0] >= target_distances[0]:
                self.y_axis.step()
            elif current_distances[0] * target_distances[1] <= current_distances[1] * target_distances[0]:
                self.x_axis.step()
            else:
                self.y_axis.step()

            current_distances = abs(self.current_location - start_location)
            time.sleep(seconds_per_step)
