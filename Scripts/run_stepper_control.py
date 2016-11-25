#!/usr/bin/env python3

import sys

import Motors
import StepperControl

# Commandline arguments
first_motor_steps = int(sys.argv[1])
second_motor_steps = int(sys.argv[2])
sum_of_rps = float(sys.argv[3])

# Script body
first_motor = Motors.large_stepper_motor([17, 22, 23, 24])
second_motor = Motors.large_stepper_motor([7, 8, 9, 10])
both_motors = StepperControl.StepperMotorPair(first_motor, second_motor)
both_motors.step_by(first_motor_steps, second_motor_steps, sum_of_rps)
