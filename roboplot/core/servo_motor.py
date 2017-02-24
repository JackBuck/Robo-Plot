"""This module defines the servo motor GPIO connection"""

import warnings

import wiringpi

# TODO Wrap wiringpi and put this line in the wrapper
wiringpi.wiringPiSetupGpio()  # Setup wiringpi

# TODO: How specific is this to the ServoMotor? Should it go in the wiringpi wrapper too? Or should the servo class
#       be a singleton and claim unique access to the wiringpi pwm?
# TODO: Ask Luke to explain these three lines...
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)  # Set PWM mode as mark space (as opposed to balanced - the default)
PWM_RANGE = 500
wiringpi.pwmSetRange(PWM_RANGE)  # Set PWM range (range of duty cycles)
wiringpi.pwmSetClock(765)  # Set PWM clock divisor


# Note: PWM Frequency = 19.2MHz / (PWM_DIVISOR * PWM_RANGE)

class Position:
    """
    A position on the servo motor.
    This class maps the required pwm output to the realised servo motor angle.
    """

    def __init__(self, scaled_pwm_output, degrees):
        """
        Defines a position on the servo motor.

        Args:
            scaled_pwm_output (float): The scaled pwm output. When multiplied by the pwm range set in wiringpi,
                                       this gives the pwm output passed to wiringpi.pwmWrite(...).
            degrees (float): The angle realised by the servo motor when this pwm is applied.
        """
        self.pwm_output = scaled_pwm_output
        self.degrees = degrees


class ServoMotor:
    def __init__(self, gpio_pin: int = 18,
                 min_position: Position = Position(0, 0),
                 max_position: Position = Position(1, 180)):
        """
        Create a servo motor driver.

        Args:
            gpio_pin (int): the BCM gpio pin (should be 18 since this is the only hardware pwm pin)
            min_position (Position): the minimum position attainable by the servo motor
            max_position (Position): the maximum position attainable by the servo motor
        """

        if not gpio_pin == 18:
            warnings.warn("Setting up servo motor on a pin other than 18. BCM pin 18 is the only hardware pwm pin.")

        self._gpio_pin = gpio_pin
        wiringpi.pinMode(gpio_pin, wiringpi.PWM_OUTPUT)  # Set SERVO pin as PWM output
        wiringpi.pwmWrite(gpio_pin, 0)  # Turn output off

        self._min_position = min_position
        self._max_position = max_position

    def rotate_to(self, degrees: float) -> None:
        """
        Rotate to the specified angle.

        Args:
            degrees: the angle in degrees to which to turn the servo
        """
        assert self.angle_is_in_range(degrees), "Requested angle is outside the servo motor's range!"

        degrees_range = self._max_position.degrees - self._min_position.degrees
        proportion = (degrees - self._min_position.degrees) / degrees_range

        pwm_range = self._max_position.pwm_output - self._min_position.pwm_output
        required_output = int((self._min_position.pwm_output + proportion * pwm_range) * PWM_RANGE)

        print(required_output)
        wiringpi.pwmWrite(self._gpio_pin, required_output)

    def angle_is_in_range(self, degrees):
        return self.min_degrees <= degrees <= self.max_degrees

    def disengage(self):
        # TODO: Does this method work? Or does our servo still retain its position?
        wiringpi.pwmWrite(self._gpio_pin, 0)

    @property
    def min_degrees(self):
        return self._min_position.degrees

    @property
    def max_degrees(self):
        return self._max_position.degrees
