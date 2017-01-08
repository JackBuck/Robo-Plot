"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also where the GPIO pins used for each piece of hardware are defined.
"""

import roboplot.core.gpio_connections as gpio_connections
import roboplot.core.stepper_control as stepper_control

# Direct GPIO connections
x_axis_motor = gpio_connections.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = gpio_connections.large_stepper_motor(gpio_pins=(19, 26, 20, 21))

# Higher level objects
x_axis = stepper_control.Axis(x_axis_motor, lead=8)
y_axis = stepper_control.Axis(y_axis_motor, lead=8)
both_axes = stepper_control.AxisPair(x_axis, y_axis)
