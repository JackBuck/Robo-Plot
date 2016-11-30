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
    def __init__(self, total_length: float, parameterisation):
        """ Define a curve.

        Args:
            total_length (float): The total length of the path in MILLIMETRES
            parameterisation (callable): The parameterisation of the path by arc length (in MILLIMETRES). This should
                                         take a numpy.nd array to a numpy.nd array.
        """
        self.total_length = total_length
        self.parameterisation = parameterisation

    def to_series_of_points(self, interval_millimetres: float) -> np.ndarray:
        """Express the path by a series of points.

        WARNING: The output does not include the last point in the path.
        This is because:
         * If you are chaining paths together, most of the time you won't want the last point, since it will be the
           first point of the next path,
         * This is how python's range and numpys arange functions behave (so it's a python-intuitive behaviour).

        Args:
            interval_millimetres: The size of each interval (in MILLIMETRES)

        Returns:
            np.ndarray: A list of pairs of points (in MILLIMETRES) to which to move the motors.

        """
        parameter = np.arange(0, self.total_length, interval_millimetres, dtype=float)
        return self.parameterisation(parameter)


class LineSegment:
    def __init__(self, start, end):
        """Define a line segment.

        If the line is to be evaluated at multiple points at once then it is recommended to pass the start and end
        parameters as numpy column vectors.

        Args:
            start: The 2D start point (in MILLIMETRES).
            end: The 2D end point (in MILLIMETRES).

        Returns:
            LineSegment: The line segment.

        """
        self.start = start
        self.end = end
        self.total_length = np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length: float) -> float:
        """Evaluate a point on the line at a particular arc length

        Args:
            arc_length (float): The distance(s) along the line at which to evaluate the line.

        Returns:
            float: The point(s) corresponding to the supplied arc lengths.

        """
        t = arc_length / self.total_length
        return (1 - t) * self.start + t * self.end

    def curve(self):
        return Curve(self.total_length, lambda s: self.evaluate_at(s))
