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
    parser = argparse.ArgumentParser(description='Draw a circle.')
    parser.add_argument('-c', '--centre', metavar=('y', 'x'), nargs=2, type=float, default=[150, 100],
                        help='the centre (y,x) of the circle in millimetres (default: %(default)smm)')
    parser.add_argument('-r', '--radius', type=float, default=30,
                        help='the radius of the circle in millimetres (default %(default)smm)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float,
                        default=hardware.plotter.default_pen_speed,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Draw a circle
    circle = curves.Circle(args.centre, args.radius)

    time.sleep(args.wait)

    hardware.plotter.home()
    start_time = time.time()
    hardware.plotter.draw(curve_list=circle, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    print(2 * np.pi * args.radius / args.pen_millimetres_per_second)

finally:
    hardware.cleanup()
