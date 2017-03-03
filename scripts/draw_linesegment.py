#!/usr/bin/env python3

import argparse
import time

import numpy as np

import context
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Draw a line segment.')
    parser.add_argument('-f', '--first-point', metavar=('y', 'x'), nargs=2, type=float, default=[50, 50],
                        help='the first point (y,x) of the line segment, in millimetres (default: %(default)smm)')
    parser.add_argument('-l', '--last-point', metavar=('y', 'x'), nargs=2, type=float, default=[125, 75],
                        help='the last point (y,x) of the line segment, in millimetres (default: %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Draw a line segment
    line_segment = curves.LineSegment(args.first_point, args.last_point)

    time.sleep(args.wait)

    hardware.both_axes.home()
    start_time = time.time()
    hardware.both_axes.follow(curve=line_segment, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    distance_travelled = np.linalg.norm((args.first_point[0] - args.last_point[0],
                                         args.first_point[1] - args.last_point[1]))
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    hardware.cleanup()
