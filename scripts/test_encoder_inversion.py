#!/usr/bin/env python3

import argparse

import context
import roboplot.core.hardware as hardware
from roboplot.core.stepper_control import Axis

parser = argparse.ArgumentParser(
    description='Determine whether the encoders need to be inverted in the hardware module.'
                'The script will move the robot forwards and backwards in both axes, and print a summary.')

parser.parse_args()


def TestEncoder(axis: Axis, axis_name: str):
    initial_expected_location = axis.expected_location
    initial_current_location = axis.current_location

    num_steps_in_10mm = int(10 / axis.millimetres_per_step)

    axis.forwards = True
    for i in range(num_steps_in_10mm):
        axis.step()

    change_in_expected_location = axis.expected_location - initial_expected_location
    change_in_current_location = axis.current_location - initial_current_location
    needs_inverting = change_in_expected_location * change_in_current_location < 0

    if change_in_current_location == 0:
        message = '{}: No movement detected on encoder!'.format(axis_name)
    else:
        message = '{}: Encoder needs inverting = {}'.format(axis_name, needs_inverting)

    print(message)


try:
    TestEncoder(hardware.x_axis, 'x-axis')
    TestEncoder(hardware.y_axis, 'y-axis')

finally:
    hardware.cleanup()
