"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also
  * where the GPIO pins used for each piece of hardware are defined,
  * where all initialisation of the hardware is performed (e.g. starting the encoder threads).
"""

import roboplot.core.encoders as encoders
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control

# Direct GPIO connections
x_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(19, 26, 20, 21))

small_stepper_1 = stepper_motors.small_stepper_motor(gpio_pins=(5, 6, 12, 16))
small_stepper_2 = stepper_motors.small_stepper_motor(gpio_pins=(2, 3, 4, 17))

x_axis_encoder = encoders.AxisEncoder(gpio_pins=(0, 1), positions_per_revolution=96, thread_name="x axis encoder")
x_axis_encoder.start()
y_axis_encoder = encoders.AxisEncoder(gpio_pins=(14, 15), positions_per_revolution=96, thread_name="y axis encoder")
y_axis_encoder.start()

# Higher level objects
x_axis = stepper_control.Axis(x_axis_motor, lead=8)
y_axis = stepper_control.Axis(y_axis_motor, lead=8)
both_axes = stepper_control.AxisPair(x_axis, y_axis)
