#!/usr/bin/env python3

import argparse

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    parser = argparse.ArgumentParser(description='Rotate the servo motor to a specified angle.')
    parser.add_argument('degrees', type=float,
                        help="The angle in degrees to which to rotate."
                             "This should be between {0:d} and {1:d}".format(hardware.servo.min_degrees,
                                                                             hardware.servo.max_degrees))
    args = parser.parse_args()

    hardware.servo.rotate_to(args.degrees)

finally:
    GPIO.cleanup()
