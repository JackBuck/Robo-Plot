#!/usr/bin/env python3

import argparse
import time

import context
import roboplot.core.hardware as hardware
import roboplot.svg.svg_parsing as svg
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Draw an svg file.')
    parser.add_argument('-r', '--resolution', type=float, default=1,
                        help='the resolution in millimetres to use when splitting the image into linear moves ('
                             'default: %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')
    parser.add_argument('filepath', type=str,
                        help='a (relative or absolute) path to the svg file')

    args = parser.parse_args()

    # Draw the svg
    svg_curves = svg.parse(args.filepath)

    time.sleep(args.wait)

    hardware.both_axes.home()

    start_time = time.time()

    distance_travelled = 0
    for curve in svg_curves:
        hardware.both_axes.follow(curve, pen_speed=args.pen_millimetres_per_second, resolution=args.resolution)
        distance_travelled += curve.total_millimetres

    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')  # Admittedly, this relies on calculations performed by the objects we're testing...
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    GPIO.cleanup()
