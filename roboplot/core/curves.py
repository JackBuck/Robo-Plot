"""
Defines the curves which Robo-Plot is capable of drawing.

All distances in the module are expressed in MILLIMETRES.
"""

import numpy as np
import svgpathtools as svg


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
        self.start = np.reshape(start, 2)
        self.end = np.reshape(end, 2)

    @property
    def total_millimetres(self) -> float:
        return np.linalg.norm(self.end - self.start)

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = arc_length.reshape(-1, 1)  # Make it a column vector
        t = arc_length / self.total_millimetres
        return (1 - t) * self.start + t * self.end


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
        radians = deg2rad(self.end_degrees - self.start_degrees)
        return abs(radians) * self.radius

    def evaluate_at(self, arc_length: np.ndarray) -> np.ndarray:
        arc_length = np.reshape(arc_length, [-1, 1])  # Make column vector
        radians = arc_length / self.radius + deg2rad(self.start_degrees)
        points = np.hstack((np.cos(radians), np.sin(radians)))
        points = self.radius * points + self.centre
        return points


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


# TODO: Consider replacing these methods with an Angle class...
# (then the conversions would be available wherever the Angle is used)
def deg2rad(degrees):
    """Convert values in degrees to radians."""
    return degrees * np.pi / 180


def rad2deg(radians):
    """Convert values in radians to degrees."""
    return radians * 180 / np.pi


# TODO: Allow for translations, rotations, shears, reflections... (i.e. an arbitrary 3x3 transformation matrix)
# The difficulty here will be to make sure you've got all the ways of transforming the shape...
# Maybe iterate up 'parent' elements, looking for the transform attribute at each one? (and ViewBox, height & width)
class SVGPath(Curve):
    """A curve which wraps an svgpathtools.Path object."""

    def __init__(self, path: svg.Path, mm_per_unit: float = 1):
        """
        Create a wrapper around an svgpathtools.Path.

        Args:
            path (svg.Path): The svg path to wrap.
            mm_per_unit (float): The scale factor for both axes. This should be such that a point (x,y) in user space
                                 maps to a point mm_per_unit*(x,y) in millimetres.
                                 Different scale factors for each axis is not supported.
        """
        self._path = path
        self._mm_per_unit = mm_per_unit

    @property
    def total_millimetres(self):
        return self._path.length() * self._mm_per_unit

    def evaluate_at(self, arc_length) -> np.ndarray:
        # First use ilength(...) to map path lengths to the built-in parameterisation
        t_values = [self._path.ilength(s) for s in np.array(arc_length) / self._mm_per_unit]

        # Then evaluate the curve at these points
        points_as_complex = np.array([self._path.point(t) for t in t_values]) * self._mm_per_unit
        return np.column_stack([np.real(points_as_complex), np.imag(points_as_complex)])
