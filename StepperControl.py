"""Stepper Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES or STEPS.

"""

import numpy as np

# TODO: Refactor this into an axis object?
#       The control theory would ideally happen at an axis level (though not strictly necessary) whilst the shape
#       drawing layer needs to translate mm into steps. However, the lead isn't a property of the shape - it is more
#       closely linked to the motor!!
#        - Maybe wrap each the motor in an axis object? Then change StepperMotorPair to axis_pair?
#        - Alternatively, have some sort of a 'coordinator' class which takes two axis objects, links the inner motor
#          objects and translates the curve into steps. Then the control theory remains in terms of numbers of steps.

first_axis_lead = 8
second_axis_lead = 8


class StepperMotorPair:
    def follow(self, curve):  # TODO: This is a hack -- see above!! (need to remove dependence on lead)
        points = curve.to_series_of_points()
        points = points.T / [first_axis_lead, second_axis_lead]
        previous_pt = points[0]
        for pt in points.T[1:]:
            difference = pt - previous_pt
            self.step_by(difference)
            previous_pt = pt

    def step_by(self, first_motor_steps, second_motor_steps, sum_of_rps):
        # TODO: Implemented on another branch (issue #5) -- merge it once that pull request has been approved.
        pass


# TODO: Make Curve an abstract class, and have shapes deriving from it?
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

    def to_series_of_points(self, interval_size: float) -> np.ndarray:
        """Express the path by a series of points.

        WARNING: The output does not include the last point in the path.
        This is because:
         * If you are chaining paths together, most of the time you won't want the last point, since it will be the
           first point of the next path,
         * This is how python's range and numpys arange functions behave (so it's a python-intuitive behaviour).

        Args:
            interval_size: The size of each step (in MILLIMETRES)

        Returns:
            np.ndarray: A list of pairs of points (in MILLIMETRES) to which to move the motors.

        """
        parameter = np.arange(0, self.total_length, interval_size, dtype=float)
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
