"""Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time

import numpy as np

import Motors


class StepperMotorPair:
    """Represents a synchronised pair of stepper motors."""

    def __init__(self, first_motor: Motors.StepperMotor, second_motor: Motors.StepperMotor):
        """
        Initialise a synchronised pair of stepper motors.

        Currently there is no implementation for synchronising motors with different step sizes.

        Args:
            first_motor: The first stepper motor
            second_motor: The second stepper motor
        """
        if first_motor.steps_per_revolution != second_motor.steps_per_revolution:
            raise NotImplementedError('There is currently no implementation for synchronising motors with different '
                                      'step sizes.')

        self._first_motor = first_motor
        self._second_motor = second_motor

    def step_by(self, first_motor_steps: int, second_motor_steps: int, sum_of_rps: float) -> None:
        """
        Steps the motors as close to linearly as possible by the specified amounts.

        Supply negative numbers of steps to achieve motion in the opposite direction.

        Args:
            first_motor_steps: The number of steps to advance the first motor.
            second_motor_steps: The number of steps to advance the second motor.
            sum_of_rps: The sum of the revolutions per second of the motors. While unnatural in an API, this is what
                        is easiest on the 'inside'. It will be changed once we know how we want to call this method.

        Returns:
            None

        """
        self._first_motor.clockwise = first_motor_steps >= 0
        first_motor_steps = abs(first_motor_steps)

        self._second_motor.clockwise = second_motor_steps >= 0
        second_motor_steps = abs(second_motor_steps)

        # We are restricting to the case where both motors have the same number of step per revolution
        seconds_per_step = 1 / (sum_of_rps * self._first_motor.steps_per_revolution)

        # TODO: Refactor this once we have encoders
        first_motor_step_count = 0
        second_motor_step_count = 0

        while True:
            if first_motor_step_count * second_motor_steps <= second_motor_step_count * first_motor_steps:
                self._first_motor.step()
                first_motor_step_count += 1
            else:
                self._second_motor.step()
                second_motor_step_count += 1

            if first_motor_step_count == first_motor_steps and second_motor_step_count == second_motor_steps:
                break

            time.sleep(seconds_per_step)

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

