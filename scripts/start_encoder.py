#!/usr/bin/env python3

import argparse
import time

import context
import roboplot.core.hardware as hardware

parser = argparse.ArgumentParser(description='Start an encoder.')
parser.add_argument('encoder', type=str, choices=('x', 'y'), nargs='?', default='x',
                    help='the encoder to run (default: %(default)s)')
parser.add_argument('-r', '--refresh-frequency', type=float, default=24,
                    help='the refresh rate / Hz (default: %(default)s)')

args = parser.parse_args()

if args.encoder is "x":
    encoder = hardware.x_axis_encoder
elif args.encoder is "y":
    encoder = hardware.y_axis_encoder
else:
    raise ValueError("Input encoder must be 'x', or 'y'.")  # The argument parser should stop us from getting here

try:
    print("Press ctrl-C to exit...")
    while True:
        print("\r{0: 7.1f} degrees".format(encoder.revolutions * 360), end='')
        time.sleep(1/float(args.refresh_frequency))
except KeyboardInterrupt:
    pass
finally:
    encoder.exit_thread()
    print("\nProgram Ended")
