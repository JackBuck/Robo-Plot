#!/usr/bin/env python3

import sys
import time

import numpy as np

import Motors
import StepperControl

# Commandline arguments
x_centre = float(sys.argv[1])
y_centre = float(sys.argv[2])
radius = float(sys.argv[3])
pen_millimetres_per_second = float(sys.argv[4])
initial_sleep = float(sys.argv[5])

# Script body
x_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([22, 23, 24, 25]), lead=8)
y_axis = StepperControl.Axis(motor=Motors.large_stepper_motor([19, 26, 20, 21]), lead=8)
both_motors = StepperControl.AxisPair(x_axis, y_axis)

time.sleep(initial_sleep)

start_time = time.time()

both_motors.follow(curve=StepperControl.Circle(centre=np.array([x_centre, y_centre]), radius=radius),
                   pen_speed=pen_millimetres_per_second)

end_time = time.time()
print('Elapsed: ', end='')
print(end_time - start_time)
print('Predicted: ', end='')
print(2 * np.pi * radius / pen_millimetres_per_second)
