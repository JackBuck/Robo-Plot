"""Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time

import numpy as np

import Motors


class Axis:
    def __init__(self, motor: Motors.StepperMotor, lead: float):
        """
        Creates an Axis.

        Args:
            motor (Motors.StepperMotor): The stepper motor driving the axis.
            lead (float): The lead of the axis, in millimetres per revolution of the motor.
        """
        self.motor = motor
        self.lead = lead

    @property
    def millimetres_per_step(self):
        return self.lead / self.motor.steps_per_revolution


class AxisPair:
    def __init__(self, x_axis: Axis, y_axis: Axis):
        self.x_axis = x_axis
        self.y_axis = y_axis

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
        previous_pt = points[0]
        for pt in points.T[1:]:
            difference = pt - previous_pt
            self.move_linearly(difference[0], difference[1], pen_speed)
            previous_pt = pt

    def move_linearly(self, x_millimetres: float, y_millimetres: float, pen_speed: float) -> None:
        """
        Steps the motors as close to linearly as possible to achieve the specified axis displacements.

        Supply negative displacements to achieve motion in the opposite direction.

        Args:
            x_millimetres (float): The displacement to move the first axis (in MILLIMETRES)
            y_millimetres (float): The displacement to move the second axis (in MILLIMETRES)
            pen_speed (float): The target speed of the pen (in MILLIMETRES / SECOND).

        """
        # TODO: A lot of this method needs refactoring so that it reads more naturally (i.e. so that we don't keep
        # digging into the Axis.motor field).

        # Convert to steps
        x_steps = x_millimetres / self.x_axis.millimetres_per_step
        y_steps = y_millimetres / self.y_axis.millimetres_per_step

        # Address direction
        self.x_axis.motor.clockwise = x_steps >= 0
        x_steps = abs(x_steps)

        self.y_axis.motor.clockwise = y_steps >= 0
        y_steps = abs(y_steps)

        # Compute the wait time
        pen_millimetres = np.linalg.norm([x_millimetres, y_millimetres])
        total_seconds = pen_millimetres / pen_speed
        total_steps = x_steps + y_steps
        seconds_per_step = total_seconds / total_steps

        # Step the motors
        # TODO: Refactor this once we have encoders
        x_step_count = 0
        y_step_count = 0

        while not (x_step_count == x_steps and y_step_count == y_steps):
            if x_step_count == x_steps:
                self.y_axis.motor.step()
                y_step_count += 1
            elif x_step_count * y_steps <= y_step_count * x_steps:
                self.x_axis.motor.step()
                x_step_count += 1
            else:
                self.y_axis.motor.step()
                y_step_count += 1

            time.sleep(seconds_per_step)


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
        self.centre = centre.reshape(2)
        self.radius = radius

    @property
    def total_millimetres(self):
        return 2 * np.pi * self.radius

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = arc_length.reshape(-1, 1)  # Make column vector
        radians = arc_length / self.total_millimetres
        points = np.hstack((np.cos(radians), np.sin(radians)))
        points = self.radius * points + self.centre
        return points

