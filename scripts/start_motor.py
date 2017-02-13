#!/usr/bin/env python3

import context
from roboplot.core.hardware import x_axis_motor
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    x_axis_motor.start(duration=60, rps=0.01)

finally:
    GPIO.cleanup()
