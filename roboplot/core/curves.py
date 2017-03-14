"""
Defines the curves which Robo-Plot is capable of drawing.

All distances in the module are expressed in MILLIMETRES.
"""

import numpy as np


# TODO: Add functionality to chain svg_curves
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
        """Express the curve by a series of points.

        Args:
            interval_millimetres (float): The size of each interval (in MILLIMETRES)
            include_last_point (bool): If true then the series of points will include the last point on the curve.
                                       Otherwise it will not, which is useful when chaining svg_curves.

        Returns:
            np.ndarray: An nx2 matrix whose ith row is the ith point (in MILLIMETRES) to which to move the axes.

        """
        arc_lengths = np.arange(0, self.total_millimetres, interval_millimetres, dtype=float)

        if include_last_point:
            arc_lengths = np.append(arc_lengths, self.total_millimetres)

        return self.evaluate_at(arc_lengths)

    def get_start_point(self):
        """
        This method should be overridden in derived classes to return the coordinates on the curve at (a) given
        position(s).

        Returns:
            np.ndarray: An nx2 matrix the first point in the curve.

               """
        raise NotImplementedError("The parameterisation method must be overridden in derived classes.")


class LineSegment(Curve):
    def __init__(self, start: np.ndarray, end: np.ndarray):
        """Define a line segment.

        Args:
            start (np.ndarray): The 2D start point (in MILLIMETRES).
            end (np.ndarray): The 2D end point (in MILLIMETRES).

        Returns:
            LineSegment: The line segment.

        """
        self.start = np.reshape(start, 2)
        self.end = np.reshape(end, 2)

    @property
    def total_millimetres(self) -> float:
        return np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = np.reshape(arc_length, (-1, 1))  # Make it a column vector
        with np.errstate(divide='ignore', invalid='ignore'):
            t = arc_length / self.total_millimetres
            t[np.isnan(t)] = 0
        return (1 - t) * self.start + t * self.end

    def get_start_point(self):
        return self.start


class CircularArc(Curve):
    def __init__(self, centre: np.ndarray, radius: float, start_degrees: float, end_degrees: float):
        """
        Define a circular arc.

        Note that the direction the arc is traversed can be reversed by switching the start_degrees and end_degrees
        arguments.

        Args:
            centre (np.ndarray): A 2-element vector specifying the centre of the circle (in MILLIMETRES)
            radius (float): The radius of the circle (in MILLIMETRES)
            start_degrees (float): The start angle (in DEGREES)
            end_degrees (float): The end angle (in DEGREES)
        """
        self.centre = np.reshape(centre, 2)
        self.radius = radius
        self.start_degrees = start_degrees
        self.end_degrees = end_degrees

    @property
    def total_millimetres(self):
        radians = np.deg2rad(self.end_degrees - self.start_degrees)
        return abs(radians) * self.radius

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        if self.radius == 0:
            return np.copy(self.centre.reshape(1,2))
        else:
            arc_length = np.reshape(arc_length, [-1, 1])  # Make column vector
            radians = arc_length / self.radius + np.deg2rad(self.start_degrees)
            points = np.hstack((np.sin(radians), np.cos(radians)))  # (y,x)
            points = self.radius * points + self.centre
            return points

    def get_start_point(self):
        return np.array([self.radius * np.cos(deg2rad(self.start_degrees)), self.radius * np.sin(deg2rad(self.start_degrees))] + self.centre)


class Circle(CircularArc):
    def __init__(self, centre: np.ndarray, radius: float):
        """
        Define a circle.

        Args:
            centre (np.ndarray): A 2-element vector specifying the centre of the circle (in MILLIMETRES).
            radius (float): The radius of the circle (in MILLIMETRES).
        """
        CircularArc.__init__(self,
                             centre=centre,
                             radius=radius,
                             start_degrees=0,
                             end_degrees=360)
