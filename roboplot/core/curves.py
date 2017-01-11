"""
Defines the curves which Robo-Plot is capable of drawing.

All distances in the module are expressed in MILLIMETRES.
"""

import numpy as np


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
