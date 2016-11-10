"""Drive Control Module

This module controls the 2D drive system for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""

import numpy as np


class Path:
    def __init__(self, total_length: float, parameterisation):
        """ Define a path.

        Args:
            total_length: The total length of the path in MILLIMETRES
            parameterisation: The parameterisation of the path by arc length (in MILLIMETRES)
        """
        self.total_length = total_length
        self.parameterisation = parameterisation

    def to_line_segments(self, step_size: float):
        """Convert a curvy path to a series of line segments.

        WARNING: The output does not include the last point in the path.
        This is because:
         * If you are chaining paths together, most of the time you won't want the last point, since it will be the
           first point of the next path,
         * This is how pythons range and numpys arange functions behave (so it's a python-intuitive behaviour).

        Args:
            step_size: The size of each step (in MILLIMETRES)

        Returns:
            A list of pairs of points (in MILLIMETRES) to which to move the motors.

        """
        parameter = np.arange(0, self.total_length, step_size, dtype=float)
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
            Path: The line segment.

        """
        self.start = start
        self.end = end
        self.total_length = np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length):
        """Evaluate a point on the line at a particular arc length

        Args:
            arc_length: The distance(s) along the line at which to evaluate the line.

        Returns:
            The point(s) corresponding to the supplied arc lengths.

        """
        t = arc_length / self.total_length
        return (1-t)*self.start + t*self.end

    def path(self):
        return Path(self.total_length, lambda s: self.evaluate_at(s))
