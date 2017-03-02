import itertools
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
    paths, _, svg_attributes_dict = svg.svg2paths2(filepath)
    setsofsubpaths = [p.continuous_subpaths() for p in paths]
    paths = itertools.chain.from_iterable(setsofsubpaths)

    svg_attributes = SvgAttributes(svg_attributes_dict)
    if svg_attributes.is_portrait:
        return [SVGPath(path, svg_attributes.scale_factor) for path in paths]
    else:
        return [SVGPathRotatedBy90Degrees(path, svg_attributes.scale_factor, svg_attributes.height) for path in paths]


class SvgAttributes:
    """Extracts information from a dictionary of attributes on the svg element of an svg document."""

    def __init__(self, svg_attributes):
        """
        Initialise the attributes object.

        This method
          - raises an exception if the height and width of the document are not expressed in millimetres,
          - raises a warning if the scale factors for the two axes are not sufficiently similar.

        Args:
            svg_attributes (dict): a dictionary of svg attributes, including the 'width', 'height' and 'viewBox'
        """
        self.width = self._get_millimetres(svg_attributes['width'])
        self.height = self._get_millimetres(svg_attributes['height'])
        self.viewbox = ViewBox(svg_attributes['viewBox'])

        self._warn_if_scale_factors_not_equal()

    @staticmethod
    def _get_millimetres(string):
        """Extract a value in millimetres from a string formatted like '40mm'."""
        match = re.match(r'^(?P<number>\d+)(?P<unit>[A-Za-z]*)$', string)
        assert match.group('unit') == 'mm'  # For the moment, just throw if it's not millimetres
        return float(match.group('number'))

    def _warn_if_scale_factors_not_equal(self):
        tol = 0.001
        scale_factors = self._scale_factors
        if abs(scale_factors[1] - scale_factors[0]) > tol:
            warnings.warn("x and y scale factors differ by more than the allowed tolerance ({:f})".format(tol))

    @property
    def _scale_factors(self):
        scale_width = self.width / self.viewbox.width
        scale_height = self.height / self.viewbox.height
        return scale_width, scale_height

    @property
    def scale_factor(self):
        """
        The scale factor for the document.

        That is, the number the scale factor, s, such that for a point p in document units, s*p is in millimetres.
        """
        return np.mean(self._scale_factors)

    @property
    def is_portrait(self):
        return self.height >= self.width


class ViewBox:
    """Represents the viewBox attribute of the 'svg' element in the document."""

    def __init__(self, attribute):
        dimensions = tuple(map(float, attribute.split()))
        self.min_x = dimensions[0]
        self.min_y = dimensions[1]
        self.width = dimensions[2]
        self.height = dimensions[3]


class SVGPath(Curve):
    """A curve which wraps an svgpathtools.Path object."""

    _evaluation_tolerance_mm = 0.01

    def __init__(self, path: svg.Path, mm_per_unit: float):
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
        t_values = [self._path.ilength(s, s_tol=tol)
                    for s in np.array(arc_length, copy=False, ndmin=1) / self._mm_per_unit]

        # Then evaluate the curve at these points
        points_as_complex = np.array([self._path.point(t) for t in t_values]) * self._mm_per_unit
        return np.column_stack(self._complex_to_yx(points_as_complex))

    @staticmethod
    def _complex_to_yx(points_as_complex):
        return np.imag(points_as_complex), np.real(points_as_complex)


class SVGPathRotatedBy90Degrees(SVGPath):
    """A curve which wraps an svgpathtools.Path object, which has been rotated by 90 degrees."""

    def __init__(self, path: svg.Path, mm_per_unit: float, document_original_height: float):
        super().__init__(path, mm_per_unit)
        self._original_height = document_original_height

    def _complex_to_yx(self, points_as_complex):
        unrotated = SVGPath._complex_to_yx(points_as_complex)
        return unrotated[1], self._original_height - unrotated[0]
