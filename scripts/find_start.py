#!/usr/bin/env python3

import argparse

import roboplot.core.hardware as hardware
import roboplot.imgproc.start_end_detection as start_end_detection
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Move around the paper and find green')

    parser.add_argument('-m', '--minsize', type=float, default=10,
                        help='the minimum size of green to be detected')

    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')

    args = parser.parse_args()

    hardware.plotter.home()
    centre = start_end_detection.find_green_triangle(args.minsize)
    centre, photo = start_end_detection.find_green_centre(centre, args.minsize)

finally:
    GPIO.cleanup()

print("Done")
