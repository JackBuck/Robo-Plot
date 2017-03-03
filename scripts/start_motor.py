#!/usr/bin/env python3

import argparse
import time

import context
import roboplot.core.hardware as hardware


try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Run the x-axis motor for a certain period of time.')
    parser.add_argument('-t', '--time', type=float, default=5,
                        help='the duration, in seconds, for which to run (default: %(default)smm/s)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='revolutions_per_second', type=float, default=2,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')

    args = parser.parse_args()

    # Script body
    time.sleep(args.wait)
    hardware.x_axis_motor.start(duration=5, rps=args.revolutions_per_second)

finally:
    hardware.cleanup()
