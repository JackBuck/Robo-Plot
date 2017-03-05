"""This module defines the servo motor GPIO connection"""

import roboplot.core.gpio.wiringpi_wrapper as wiringpi_wrapper


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
            # Can't do this more naturally because I don't fully understand the scope of the wiringpi.pwmSetMode,
            # pwmSetRange and pwmSetClock methods.
            # I've kept the gpio_pin argument so that we can write it explicitly in the hardware class. An
            # alternative would be to make a factory method on the Servo class called create_on_pin_18() or similar.
            raise ValueError("Setting up servo motor on a pin other than 18. BCM pin 18 is the only hardware pwm pin.")

        assert 0 <= min_position <= max_position <= 1

        self._gpio_pin = gpio_pin
        wiringpi_wrapper.setup_pwm_pin_18()
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
        required_output = int(float(pwm_input) * wiringpi_wrapper.pwm_pin.pwm_range)
        wiringpi_wrapper.write_pwm_to_pin_18(required_output)

    def input_is_in_range(self, pwm_input):
        return self.min_position <= pwm_input <= self.max_position

    def stop_pwm(self):
        """Note that the servo motor will still remain engaged after the pi ceases to send a pwm signal."""
        wiringpi_wrapper.write_pwm_to_pin_18(0)
