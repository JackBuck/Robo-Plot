#!/usr/bin/env python3

import argparse
import os
import re
import time

import numpy as np
import svgpathtools as svg

import context
import roboplot.core.curves as curves
import roboplot.core.gpio.gpio_wrapper as gpio_wrapper
import roboplot.core.hardware as hardware

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Draw a stick figure constructed as a cubic Bezier curve.')
    parser.add_argument('-r', '--resolution', type=float, default=10,
                        help='the resolution in millimetres to use when splitting the image into linear moves ('
                             'default: %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Definitions
    # TODO: Put scale factor stuff in the roboplot package
    #  Note -- it isn't really supported by svgpathtools though, since there are ways to transform the paths using the
    #  <g></g> 'grouping' tokens which I do not think are extracted by svgpathtools.
    #  See: https://www.w3.org/TR/SVG11/coords.html#EstablishingANewUserSpace

    class ViewBox:
        def __init__(self, attribute):
            dimensions = tuple(map(float, attribute.split()))
            self.min_x = dimensions[0]
            self.min_y = dimensions[1]
            self.width = dimensions[2]
            self.height = dimensions[3]


    def get_millimetres(str):
        """Extract a value in millimetres from a string formatted like '40mm'."""
        match = re.match(r'^(?P<number>\d+)(?P<unit>[A-Za-z]*)$', str)
        assert match.group('unit') == 'mm'  # For the moment, just throw if it's not millimetres
        return float(match.group('number'))


    # Prep
    filepath = os.path.join(context.resources_dir, 'StickFig_Bezier.svg')
    paths, attributes, svg_attributes = svg.svg2paths2(filepath)

    width = get_millimetres(svg_attributes['width'])
    height = get_millimetres(svg_attributes['height'])
    viewbox = ViewBox(svg_attributes['viewBox'])
    scale_factors = (width / viewbox.width, height / viewbox.height)
    scale_factor = np.mean(scale_factors)

    # Draw
    time.sleep(args.wait)
    start_time = time.time()

    distance_travelled = 0
    for path in paths:
        svg_curve = curves.SVGPath(path)
        hardware.both_axes.follow(svg_curve, pen_speed=args.pen_millimetres_per_second, resolution=args.resolution)
        distance_travelled += svg_curve.total_millimetres

    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')  # Admittedly, this relies on calculations performed by the objects we're testing...
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    gpio_wrapper.clean_up()
