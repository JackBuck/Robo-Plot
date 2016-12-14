#!/usr/bin/env python3

import sys
import time

import Motors
import StepperControl


# Commandline arguments
x_millimetres = float(sys.argv[1])
y_millimetres = float(sys.argv[2])
pen_millimetres_per_second = float(sys.argv[3])

# Script body
x_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([22, 23, 24, 25]), lead=8)
y_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([19, 26, 20, 21]), lead=8)
both_motors = StepperControl.AxisPair(x_axis, y_axis)

start_time = time.time()

both_motors.move_linearly([x_millimetres, y_millimetres], pen_millimetres_per_second)

end_time = time.time()
print("Elapsed: ", end='')
print(end_time - start_time)
print("Predicted: ", end='')
print(((x_millimetres ** 2 + y_millimetres ** 2)**0.5) / pen_millimetres_per_second)
