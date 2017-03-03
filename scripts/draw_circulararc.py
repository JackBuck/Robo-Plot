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
    parser = argparse.ArgumentParser(description='Draw a circular arc.'
                                                 'Note that the circle is drawn in a clockwise direction beginning at'
                                                 'the point with greatest x value. This is consistent with our left '
                                                 'handed coordinate system where positive y points down the page.')
    parser.add_argument('-c', '--centre', metavar=('y', 'x'), nargs=2, type=float, default=[100, 100],
                        help='the centre (y,x) of the circle in millimetres (default: %(default)smm)')
    parser.add_argument('-r', '--radius', type=float, default=50,
                        help='the radius of the circle in millimetres (default: %(default)smm)')
    parser.add_argument('-i', '--interval-degrees', metavar=('start', 'end'), nargs=2, type=float, default=[0, 180],
                        help='the interval to draw in degrees (default: %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float,
                        default=hardware.plotter.default_pen_speed,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Draw a circle
    arc = curves.CircularArc(centre=args.centre,
                             radius=args.radius,
                             start_degrees=args.interval_degrees[0],
                             end_degrees=args.interval_degrees[1])

    time.sleep(args.wait)

    hardware.plotter.home()
    start_time = time.time()
    hardware.plotter.draw(curve_list=arc, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    distance_travelled = args.radius * abs(args.interval_degrees[1] - args.interval_degrees[0]) * np.pi / 180
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    GPIO.cleanup()
