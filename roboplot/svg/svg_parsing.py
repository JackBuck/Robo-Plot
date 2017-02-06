import numpy as np
import svgpathtools as svg

from roboplot.core.curves import Curve


class SVGPath(Curve):
    """A curve which wraps an svgpathtools.Path object."""

    _evaluation_tolerance_mm = 0.01

    def __init__(self, path: svg.Path, mm_per_unit):
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
        tol = self._evaluation_tolerance_mm / self._mm_per_unit
        t_values = [self._path.ilength(s, s_tol=tol) for s in np.array(arc_length) / self._mm_per_unit]

        # Then evaluate the curve at these points
        points_as_complex = np.array([self._path.point(t) for t in t_values]) * self._mm_per_unit
        return np.column_stack([np.imag(points_as_complex), np.real(points_as_complex)])  # (y,x)
