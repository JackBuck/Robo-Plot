import svgpathtools as svg

import roboplot.core.curves as curves
import roboplot.svg.svg_parsing as svg_parsing


def points_to_line_segments(points_yx, is_closed: bool):
    """
    Convert a set of points to a sequence of line segments between the points.

    Args:
        points_yx: the list/tuple/numpy array of points
        is_closed: if true then a line segment between the last and first point will be included

    Returns:
        list[curves.LineSegment]: the sequence of line segments joining the points
    """
    path_curve = [curves.LineSegment(points_yx[i - 1], points_yx[i]) for i in range(1, len(points_yx))]
    if is_closed and len(points_yx) > 0:
        path_curve.append(curves.LineSegment(points_yx[-1], points_yx[0]))
    return path_curve


def points_to_svg_line_segments(points_yx, is_closed: bool):
    """
    Convert a set of points to a sequence of line segments in an SVGPath form.

    Args:
        points_yx: the list/tuple/numpy array of points
        is_closed: if true then a line segment between the last and first point will be included

    Returns:
        SVGPath: the svg line segments joining the points
    """
    path = svg.Path()
    for i in range(1, len(points_yx)):
        path.append(svg.Line(yx_to_complex(points_yx[i - 1]), yx_to_complex(points_yx[i])))

    if is_closed and len(points_yx) > 0:
        path.append(svg.Line(yx_to_complex(points_yx[-1]), yx_to_complex(points_yx[0])))

    return svg_parsing.SVGPath(path, mm_per_unit=1)


def yx_to_complex(yx_location) -> complex:
    return complex(yx_location[1], yx_location[0])
