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

class ServoMotor:
    def __init__(self, min_position: float, max_position: float, gpio_pin: int = 18):
        """
        Create a servo motor driver.

        Args:
            gpio_pin (int): the BCM gpio pin (should be 18 since this is the only hardware pwm pin)
            min_position (float): the minimum (safe) input to the servo motor
            max_position (float): the maximum (safe) input to the servo motor
        """

        if not gpio_pin == 18:
            warnings.warn("Setting up servo motor on a pin other than 18. BCM pin 18 is the only hardware pwm pin.")

        assert 0 <= min_position <= max_position <= 1

        self._gpio_pin = gpio_pin
        wiringpi.pinMode(gpio_pin, wiringpi.PWM_OUTPUT)  # Set SERVO pin as PWM output
        wiringpi.pwmWrite(gpio_pin, 0)  # Turn output off

        self.min_position = min_position
        self.max_position = max_position

    def set_position(self, pwm_input: float) -> None:
        """
        Rotate to a specific position.

        The input is in arbitrary units.

        Args:
            pwm_input: the arbitrary input to use to set the servo orientation
        """
        assert self.input_is_in_range(pwm_input), "Requested angle is outside the servo motor's range!"
        required_output = int(float(pwm_input) * PWM_RANGE)
        wiringpi.pwmWrite(self._gpio_pin, required_output)

    def input_is_in_range(self, pwm_input):
        return self.min_position <= pwm_input <= self.max_position

    def stop_pwm(self):
        """Note that the servo motor will still remain engaged after the pi ceases to send a pwm signal."""
        wiringpi.pwmWrite(self._gpio_pin, 0)
