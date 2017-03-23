#!/usr/bin/env python3

import argparse

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    parser = argparse.ArgumentParser(description='Rotate the servo motor to a specified position.')
    parser.add_argument('position', type=float,
                        help="The position to set on the servo "
                             "(this is a proportion of the maximum pwm frequency set up on the pi). "
                             "This should be between {} and {}, or 0.".format(hardware.servo.min_position,
                                                                              hardware.servo.max_position))
    args = parser.parse_args()

    if args.position == 0:
        print('Disengaging servo... ', end='')
        hardware.servo.disengage()
        print('Success')
    else:
        print('Setting servo to {}...'.format(args.position), end='')
        hardware.servo.set_position(args.position)
        print('Success')

finally:
    #GPIO.cleanup()
    pass
