#!/usr/bin/env python3

import context
from roboplot.core import gpio_connections

try:
    a_motor = gpio_connections.large_stepper_motor(gpio_pins=[17, 22, 23, 24])
    a_motor.start(duration=60, rps=0.01)

finally:
    gpio_connections.quit_gui()
