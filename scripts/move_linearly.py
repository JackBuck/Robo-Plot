#!/usr/bin/env python3

import argparse
import time

import numpy as np

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Move the pen in a straight line using the low level linear move method.')
    parser.add_argument('y_millimetres', metavar='y', type=float,
                        help='a %(type)s for the target y displacement in millimetres')
    parser.add_argument('x_millimetres', metavar='x', type=float,
                        help='a %(type)s for the target x displacement in millimetres')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Script body
    target_duration = np.linalg.norm([args.y_millimetres, args.x_millimetres]) / args.pen_millimetres_per_second

    time.sleep(args.wait)

    start_time = time.time()
    hardware.both_axes.move_linearly(target_location=[args.y_millimetres, args.x_millimetres],
                                     target_completion_time=start_time + target_duration)
    end_time = time.time()

    # Report statistics
    print("Elapsed: ", end='')
    print(end_time - start_time)
    print("Predicted: ", end='')
    print(target_duration)

finally:
    GPIO.cleanup()
