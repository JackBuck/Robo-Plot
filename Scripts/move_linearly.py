#!/usr/bin/env python3

import sys
import time
import argparse

import Motors
import StepperControl


# Commandline arguments
parser = argparse.ArgumentParser(description='Move the pen in a straight line using the low level linear move method.')
parser.add_argument('x_millimetres', metavar='x', type=float,
                    help='a %(type)s for the target x displacement in millimetres')
parser.add_argument('y_millimetres', metavar='y', type=float,
                    help='a %(type)s for the target y displacement in millimetres')
parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                    help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
parser.add_argument('-w', '--wait', type=float, default=0,
                    help='an initial sleep time in seconds (default: %(default)s)')

args = parser.parse_args()

# Script body
x_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([22, 23, 24, 25]), lead=8)
y_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([19, 26, 20, 21]), lead=8)
both_motors = StepperControl.AxisPair(x_axis, y_axis)

start_time = time.time()

both_motors.move_linearly([args.x_millimetres, args.y_millimetres], args.pen_millimetres_per_second)

end_time = time.time()
print("Elapsed: ", end='')
print(end_time - start_time)
print("Predicted: ", end='')
print((args.x_millimetres ** 2 + args.y_millimetres ** 2) ** 0.5 / args.pen_millimetres_per_second)
