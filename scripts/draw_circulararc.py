#!/usr/bin/env python3

import argparse
import time

import numpy as np

import context
import roboplot.core.stepper_control as stepper_control
import roboplot.core.gpio_connections as gpio_connections
import roboplot.core.curves as curves

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

    # Set up the hardware
    x_axis = stepper_control.Axis(motor=gpio_connections.large_stepper_motor([22, 23, 24, 25]), lead=8)
    y_axis = stepper_control.Axis(motor=gpio_connections.large_stepper_motor([19, 26, 20, 21]), lead=8)
    both_motors = stepper_control.AxisPair(x_axis, y_axis)

    # Draw a circle
    arc = curves.CircularArc(centre=args.centre,
                             radius=args.radius,
                             start_degrees=args.interval_degrees[0],
                             end_degrees=args.interval_degrees[1])

    time.sleep(args.wait)

    start_time = time.time()
    both_motors.follow(curve=arc, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    distance_travelled = args.radius * abs(args.interval_degrees[1] - args.interval_degrees[0]) * np.pi / 180
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    gpio_connections.quit_gui()
