"""
A hardware repository.

This module defines the specific instances of the hardware classes which should be used to communicate with our
hardware.

It is also where the GPIO pins used for each piece of hardware are defined.
"""

import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.servo_motor as servo_motor
import roboplot.core.stepper_motors as stepper_motors
import roboplot.core.stepper_control as stepper_control

# Direct GPIO connections
x_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(22, 23, 24, 25))
y_axis_motor = stepper_motors.large_stepper_motor(gpio_pins=(19, 26, 20, 21))

small_stepper_1 = stepper_motors.small_stepper_motor(gpio_pins=(5, 6, 12, 16))
small_stepper_2 = stepper_motors.small_stepper_motor(gpio_pins=(2, 3, 4, 17))

servo = servo_motor.ServoMotor(gpio_pin=18,
                               min_position=servo_motor.Position(scaled_pwm_output=0.028, degrees=0),
                               max_position=servo_motor.Position(scaled_pwm_output=0.13, degrees=180))

# Higher level objects
x_axis = stepper_control.Axis(x_axis_motor, lead=8)
y_axis = stepper_control.Axis(y_axis_motor, lead=8, invert_axis=True)

if __debug__:
    both_axes = stepper_control.AxisPairWithDebugImage(y_axis, x_axis)
else:
    both_axes = stepper_control.AxisPair(y_axis, x_axis)

# TODO: Set the up and down positions at a practical session
pen = liftable_pen.LiftablePen(servo=servo, degrees_when_down=80, degrees_when_up=100)
