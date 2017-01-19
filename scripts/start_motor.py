#!/usr/bin/env python3

import context
import roboplot.core.gpio.gpio_wrapper as gpio_wrapper
from roboplot.core.hardware import x_axis_motor

try:
    x_axis_motor.start(duration=60, rps=0.01)

finally:
    gpio_wrapper.clean_up()
