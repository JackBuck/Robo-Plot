"""Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""

import numpy as np


class Axis:
    def __init__(self, motor, lead):
        """
        Creates an Axis.

        Args:
            motor (StepperMotor): The stepper motor driving the axis.
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

    def follow(self, curve, pen_velocity):
        points = curve.to_series_of_points().T
        previous_pt = points[0]
        for pt in points.T[1:]:
            difference = pt - previous_pt
            self.move_linearly(difference[0], difference[1], pen_velocity)
            previous_pt = pt

    def move_linearly(self, x_millimetres, y_millimetres, pen_velocity):
        x_steps = x_millimetres / self.x_axis.millimetres_per_step
        y_steps = y_millimetres / self.y_axis.millimetres_per_step
        # TODO: UNFINISHED!!
        # Most of this is implemented on another branch (issue #5) (in StepperMotorPair.step_by(...)) -- merge it
        # once that pull request has been approved.


# TODO: Add functionality to chain curves
class Curve:
    @property
    def total_millimetres(self):
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
    def total_millimetres(self):
        return np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = arc_length.reshape(-1, 1)  # Make it a column vector
        t = arc_length / self.total_millimetres
        return (1 - t) * self.start + t * self.end

