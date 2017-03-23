#!/usr/bin/env python3

import argparse

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Lift or drop the pen.')
    parser.add_argument('position', type=str, choices=['up', 'down'], nargs='?', default='up',
                        help='the position to set the pen (default: %(default)smm)')

    args = parser.parse_args()

    # Script body
    if args.position == 'up':
        hardware.pen.lift()
    elif args.position == 'down':
        hardware.pen.drop()
    else:
        raise ValueError('Bad input!')  # Shouldn't get here since argument parser will catch invalid arguments

finally:
    GPIO.cleanup()
