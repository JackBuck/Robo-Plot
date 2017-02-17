"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also
  * where the GPIO pins used for each piece of hardware are defined,
  * where all initialisation of the hardware is performed (e.g. starting the encoder threads).
"""

import os
import warnings

import roboplot.core.encoders as encoders
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control
import roboplot.config as config

# Decide how much real hardware to use
use_real_encoders = config.real_hardware
if use_real_encoders:
    warnings.warn("Manually disabling encoders dispite ROBOPLOT environment variable.")
    use_real_encoders = False

# Direct GPIO connections
x_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(19, 26, 20, 21))

small_stepper_1 = stepper_motors.small_stepper_motor(gpio_pins=(5, 6, 12, 16))
small_stepper_2 = stepper_motors.small_stepper_motor(gpio_pins=(2, 3, 4, 17))

_real_x_axis_encoder = encoders.Encoder(gpio_pins=(0, 1), positions_per_revolution=96, thread_name="x axis encoder")
_real_y_axis_encoder = encoders.Encoder(gpio_pins=(14, 15), positions_per_revolution=96, thread_name="y axis encoder")

# Swap in dummy objects if requested
if use_real_encoders:
    x_axis_encoder = _real_x_axis_encoder
    x_axis_encoder.start()
    y_axis_encoder = _real_y_axis_encoder
    y_axis_encoder.start()
else:
    x_axis_encoder = encoders.PretendEncoder(x_axis_motor)
    y_axis_encoder = encoders.PretendEncoder(y_axis_motor)

# Higher level objects
x_axis = stepper_control.Axis(x_axis_motor, x_axis_encoder, lead=8)
y_axis = stepper_control.Axis(y_axis_motor, y_axis_encoder, lead=8, invert_axis=True)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage(y_axis, x_axis)
else:
    both_axes = stepper_control.AxisPair(y_axis, x_axis)
