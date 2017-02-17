"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also where the GPIO pins used for each piece of hardware are defined.
"""

import roboplot.core.limit_switches as limit_switches
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control

# Direct GPIO connections
x_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(19, 26, 20, 21))
small_stepper_1 = stepper_motors.small_stepper_motor(gpio_pins=(5, 6, 12, 16))
small_stepper_2 = stepper_motors.small_stepper_motor(gpio_pins=(2, 3, 4, 17))
x_limit_switches = (limit_switches.LimitSwitch(gpio_pin=9),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=11)) # Encoder side
y_limit_switches = (limit_switches.LimitSwitch(gpio_pin=8),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=7))  # Encoder side

# Higher level objects
x_axis = stepper_control.Axis(motor=x_axis_motor, lead=8, limit_switch_pair=x_limit_switches)
y_axis = stepper_control.Axis(motor=y_axis_motor, lead=8, limit_switch_pair=y_limit_switches)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage(y_axis, x_axis)
else:
    both_axes = stepper_control.AxisPair(y_axis, x_axis)
