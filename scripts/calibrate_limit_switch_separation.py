#!/usr/bin/env python3

import argparse

import numpy as np

import roboplot.core.hardware as hardware
from roboplot.core.stepper_control import Axis
from roboplot.core.gpio.gpio_wrapper import GPIO


def discover_switch_separation(axis: Axis):
    axis.limit_switch_separation = np.inf
    axis.home()
    hit_location = axis.explore_limit_switch(forwards=not axis.home_position.forwards)
    return abs(hit_location - axis.home_position.location)


try:
    parser = argparse.ArgumentParser(description='Determine the limit switch separation.')
    args = parser.parse_args()

    x_switch_separation = discover_switch_separation(hardware.x_axis)
    print('x-axis limit switch separation: {}'.format(x_switch_separation))

    y_switch_separation = discover_switch_separation(hardware.y_axis)
    print('y-axis limit switch separation: {}'.format(y_switch_separation))

finally:
    GPIO.cleanup()
