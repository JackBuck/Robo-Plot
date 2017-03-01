"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also where the GPIO pins used for each piece of hardware are defined.
"""

import roboplot.core.liftable_pen as liftable_pen
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

# Higher level objects
pen = liftable_pen.LiftablePen(servo=servo, position_when_down=0.03, position_when_up=0.05)

x_axis = stepper_control.Axis(x_axis_motor, lead=8)
y_axis = stepper_control.Axis(y_axis_motor, lead=8, invert_axis=True)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage(y_axis, x_axis)
else:
    both_axes = stepper_control.AxisPair(y_axis, x_axis)

plotter = plotter_module.Plotter(axes=both_axes, pen=pen)
