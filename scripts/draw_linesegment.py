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
    parser = argparse.ArgumentParser(description='Draw a line segment.')
    parser.add_argument('-f', '--first-point', metavar=('x', 'y'), nargs=2, type=float, default=[0, 0],
                        help='the first point (x,y) of the line segment, in millimetres (default: %(default)smm)')
    parser.add_argument('-l', '--last-point', metavar=('x', 'y'), nargs=2, type=float, required=True,
                        help='the last point (x,y) of the line segment, in millimetres (required)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Set up the hardware
    x_axis = stepper_control.Axis(motor=gpio_connections.large_stepper_motor([22, 23, 24, 25]), lead=8)
    y_axis = stepper_control.Axis(motor=gpio_connections.large_stepper_motor([19, 26, 20, 21]), lead=8)
    both_motors = stepper_control.AxisPair(x_axis, y_axis)

    # Draw a line segment
    line_segment = curves.LineSegment(args.first_point, args.last_point)

    time.sleep(args.wait)

    start_time = time.time()
    both_motors.follow(curve=line_segment, pen_speed=args.pen_millimetres_per_second)
    end_time = time.time()

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    distance_travelled = np.linalg.norm((args.first_point[0] - args.last_point[0],
                                         args.first_point[1] - args.last_point[1]))
    print(distance_travelled / args.pen_millimetres_per_second)

finally:
    gpio_connections.quit_gui()
