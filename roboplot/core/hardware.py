"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also where the GPIO pins used for each piece of hardware are defined.
"""

import numpy as np

import roboplot.config as config
import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.limit_switches as limit_switches
import roboplot.core.plotter as plotter_module
import roboplot.core.servo_motor as servo_motor
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control

# Direct GPIO connections
x_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(19, 26, 20, 21))

small_stepper_1 = stepper_motors.small_stepper_motor(gpio_pins=(5, 6, 12, 16))
small_stepper_2 = stepper_motors.small_stepper_motor(gpio_pins=(2, 3, 4, 17))

servo = servo_motor.ServoMotor(gpio_pin=18,
                               min_position=0.03,
                               max_position=0.12)

x_limit_switches = (limit_switches.LimitSwitch(gpio_pin=8),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=7))  # Encoder side
y_limit_switches = (limit_switches.LimitSwitch(gpio_pin=9),  # Motor side
                    limit_switches.LimitSwitch(gpio_pin=11))  # Encoder side

x_home_position = stepper_control.HomePosition(forwards=False, location=3)
y_home_position = stepper_control.HomePosition(forwards=False, location=3)

# Substitute objects
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
    motor=x_axis_motor, lead=8, limit_switch_pair=x_limit_switches, home_position=x_home_position, invert_axis=True)
y_axis = stepper_control.Axis(
    motor=y_axis_motor, lead=8, limit_switch_pair=y_limit_switches, home_position=y_home_position, invert_axis=False)

# Post initialisation actions when not running real hardware
if not config.real_hardware:
    for switch in x_limit_switches:
        switch.register_parent_axis(x_axis)

    for switch in y_limit_switches:
        switch.register_parent_axis(y_axis)

    x_axis.current_location = x_home_position.location + (10 if not x_home_position.forwards else -10)
    y_axis.current_location = y_home_position.location + (10 if not y_home_position.forwards else -10)

both_axes = stepper_control.AxisPair(y_axis, x_axis)

pen = liftable_pen.LiftablePen(servo=servo, position_when_down=0.03, position_when_up=0.05)
plotter = plotter_module.Plotter(axes=both_axes, pen=pen)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage.create_from(both_axes)
    plotter = plotter_module.PlotterWithDebugImage.create_from(plotter)
