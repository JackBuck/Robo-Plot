#!/usr/bin/env python3

import argparse
import time

import numpy as np

import context
import roboplot.core.curves as curves
import roboplot.core.gpio.gpio_wrapper as gpio_wrapper
import roboplot.core.hardware as hardware

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Draw a circular arc.')
    parser.add_argument('-c', '--centre', metavar=('x', 'y'), nargs=2, type=float, default=[0, 0],
                        help='the centre (x,y) of the circle in millimetres (default: %(default)smm)')
    parser.add_argument('-r', '--radius', type=float, required=True,
                        help='the radius of the circle in millimetres')
    parser.add_argument('-i', '--interval-degrees', metavar=('start', 'end'), nargs=2, type=float, default=[0, 360],
                        help='the interval to draw in degrees (default: %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Create the line segments defining a circle
    arc = curves.CircularArc(centre=args.centre,
                             radius=args.radius,
                             start_degrees=args.interval_degrees[0],
                             end_degrees=args.interval_degrees[1])

    time.sleep(args.wait)

    start_time = time.time()

    # Draw the circle.
    hardware.both_axes.follow(curve=arc, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    distance_travelled = args.radius * abs(args.interval_degrees[1] - args.interval_degrees[0]) * np.pi / 180
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    gpio_wrapper.clean_up()
