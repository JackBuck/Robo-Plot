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

import numpy as np

import roboplot.config as config
import roboplot.core.encoders as encoders
import roboplot.core.limit_switches as limit_switches
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control

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

x_limit_switches = (limit_switches.LimitSwitch(gpio_pin=8),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=7))  # Encoder side
y_limit_switches = (limit_switches.LimitSwitch(gpio_pin=9),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=11))  # Encoder side

_real_x_axis_encoder = encoders.Encoder(gpio_pins=(0, 1), positions_per_revolution=96, thread_name="x axis encoder")
_real_y_axis_encoder = encoders.Encoder(gpio_pins=(14, 15), positions_per_revolution=96, thread_name="y axis encoder")

x_home_position = stepper_control.HomePosition()
y_home_position = stepper_control.HomePosition()

# Swap in dummy objects if requested
if use_real_encoders:
    x_axis_encoder = _real_x_axis_encoder
    x_axis_encoder.start()
    y_axis_encoder = _real_y_axis_encoder
    y_axis_encoder.start()
else:
    x_axis_encoder = encoders.PretendEncoder(x_axis_motor)
    y_axis_encoder = encoders.PretendEncoder(y_axis_motor)

if not config.real_hardware:
    def _define_pretend_limit_switches(home_position, separation):
        assert separation > 0

        if home_position.forwards:
            switch_locations = home_position.location + np.array([-separation, 0])
        else:
            switch_locations = home_position.location + np.array([0, separation])

        return (limit_switches.PretendLimitSwitch(valid_range=(switch_locations[0], np.inf)),
                limit_switches.PretendLimitSwitch(valid_range=(-np.inf, switch_locations[1])))

    x_limit_switches = _define_pretend_limit_switches(x_home_position, 220)
    y_limit_switches = _define_pretend_limit_switches(y_home_position, 350)

# Higher level objects
x_axis = stepper_control.Axis(
    motor=x_axis_motor, encoder=x_axis_encoder, lead=8, limit_switch_pair=x_limit_switches,
    home_position=x_home_position)
y_axis = stepper_control.Axis(
    motor=y_axis_motor, encoder=y_axis_encoder, lead=8, limit_switch_pair=y_limit_switches,
    home_position=y_home_position, invert_axis=True)

# Post initialisation actions when not running real hardware
if not config.real_hardware:
    for switch in x_limit_switches:
        switch.register_parent_axis(x_axis)

    for switch in y_limit_switches:
        switch.register_parent_axis(y_axis)

    x_axis.current_location = x_home_position.location + (10 if not x_home_position.forwards else -10)
    y_axis.current_location = y_home_position.location + (10 if not y_home_position.forwards else -10)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage(y_axis, x_axis)
else:
    both_axes = stepper_control.AxisPair(y_axis, x_axis)
