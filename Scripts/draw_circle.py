#!/usr/bin/env python3

import time
import argparse

import numpy as np

import Motors
import StepperControl

# Commandline arguments
parser = argparse.ArgumentParser(description='Draw a circle.')
parser.add_argument('-c', '--centre', metavar=('x', 'y'), nargs=2, type=float, default=[0, 0],
                    help='the centre (x,y) of the circle in millimetres (default: %(default)smm)')
parser.add_argument('-r', '--radius', type=float, required=True,
                    help='the radius of the circle in millimetres')
parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                    help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
parser.add_argument('-w', '--wait', type=float, default=0,
                    help='an initial sleep time in seconds (default: %(default)s)')

args = parser.parse_args()

# Script body
x_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([22, 23, 24, 25]), lead=8)
y_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([19, 26, 20, 21]), lead=8)
both_motors = StepperControl.AxisPair(x_axis, y_axis)

circle = StepperControl.Circle(args.centre, args.radius)

time.sleep(args.wait)

start_time = time.time()
both_motors.follow(curve=circle, pen_speed=args.pen_millimetres_per_second)
end_time = time.time()

print('Elapsed: ', end='')
print(end_time - start_time)
print('Predicted: ', end='')
print(2 * np.pi * args.radius / args.pen_millimetres_per_second)
