import re
import warnings

import numpy as np
import svgpathtools as svg

from roboplot.core.curves import Curve


def parse(filepath: str):
    """
    Parses an svg file to return an iterable of SVGPaths.

    Args:
        filepath (str): curve to the svg file.

    Returns:
        an iterable of SVGPath objects.

    """
    paths, _, svg_attributes = svg.svg2paths2(filepath)
    scale_factor = _compute_scale_factor(svg_attributes)
    return [SVGPath(path, scale_factor) for path in paths]


def _compute_scale_factor(svg_attributes):
    """
    Extracts the scale factor from millimetres to document units.

    This method
      - raises an exception if the height and width of the document are not expressed in millimetres,
      - raises a warning if the scale factors for the two axes are not sufficiently similar.

    Args:
        svg_attributes: the attributes from the svg element of the document.

    Returns:
        the scale factor, s, such that for a point p in document units, s*p is in millimetres.

    """
    width = _get_millimetres(svg_attributes['width'])
    height = _get_millimetres(svg_attributes['height'])
    viewbox = ViewBox(svg_attributes['viewBox'])
    scale_factors = (width / viewbox.width, height / viewbox.height)

    tol = 0.001
    if abs(scale_factors[1] - scale_factors[0]) > tol:
        warnings.warn("x and y scale factors differ by more than the allowed tolerance ({:f})".format(tol))

    return np.mean(scale_factors)


class ViewBox:
    """Represents the viewBox attribute of the 'svg' element in the document."""
    def __init__(self, attribute):
        dimensions = tuple(map(float, attribute.split()))
        self.min_x = dimensions[0]
        self.min_y = dimensions[1]
        self.width = dimensions[2]
        self.height = dimensions[3]


def _get_millimetres(str):
    """Extract a value in millimetres from a string formatted like '40mm'."""
    match = re.match(r'^(?P<number>\d+)(?P<unit>[A-Za-z]*)$', str)
    assert match.group('unit') == 'mm'  # For the moment, just throw if it's not millimetres
    return float(match.group('number'))


class SVGPath(Curve):
    """A curve which wraps an svgpathtools.Path object."""

    _evaluation_tolerance_mm = 0.01

    def __init__(self, path: svg.Path, mm_per_unit):
        """
        Create a wrapper around an svgpathtools.Path.

        Args:
            path (svg.Path): The svg curve to wrap.
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
        # First use ilength(...) to map curve lengths to the built-in parameterisation
        tol = self._evaluation_tolerance_mm / self._mm_per_unit
        t_values = [self._path.ilength(s, s_tol=tol) for s in np.array(arc_length) / self._mm_per_unit]

        # Then evaluate the curve at these points
        points_as_complex = np.array([self._path.point(t) for t in t_values]) * self._mm_per_unit
        return np.column_stack([np.imag(points_as_complex), np.real(points_as_complex)])  # (y,x)
