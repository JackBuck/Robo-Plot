#!/usr/bin/env python3

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    for s in hardware.x_limit_switches:
        print(s.is_pressed)

    for s in hardware.y_limit_switches:
        print(s.is_pressed)

finally:
    GPIO.cleanup()
