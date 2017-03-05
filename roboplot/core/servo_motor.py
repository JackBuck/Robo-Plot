"""This module defines the servo motor GPIO connection"""

import time

import numpy as np

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

        wiringpi_wrapper.setup_pwm_pin_18(initial_value=0)
        self._last_set_position = 0
        self.min_position = min_position
        self.max_position = max_position

    def move_smoothly_to(self, target_position: float, seconds_to_take: float) -> None:
        """
        Move smoothly between the current position and the target position.

        Args:
            target_position (float): the target position for the servo motor
            seconds_to_take (float): the time in seconds to take for the move
        """
        num_positions = self._num_possible_positions_between(self._last_set_position, target_position)
        target_positions = np.linspace(self._last_set_position, target_position, num_positions)
        target_times = time.time() + np.linspace(0, seconds_to_take, num_positions)
        for i in range(num_positions):
            self.set_position(target_positions[i])
            _wait_until(target_times[i])

    def _num_possible_positions_between(self, first, second):
        """Returns the number of possible positions between two positions, including both those positions."""
        return abs(self._required_output(first) - self._required_output(second)) + 1

    def set_position(self, pwm_input: float) -> None:
        """
        Rotate to a specific position.

        The input is in arbitrary units.

        Args:
            pwm_input: the arbitrary input to use to set the servo orientation
        """
        assert self.input_is_in_range(pwm_input), "Requested angle is outside the servo motor's range!"
        wiringpi_wrapper.write_pwm_to_pin_18(self._required_output(pwm_input))
        self._last_set_position = pwm_input

    def input_is_in_range(self, pwm_input):
        return self.min_position <= pwm_input <= self.max_position

    @staticmethod
    def _required_output(pwm_input: float) -> int:
        """
        Convert a given pwm input for the servo motor to the value which should be passed to
        wiringpi_wrapper.write_pwm_to_pin_18().

        Args:
            pwm_input (float): the 'normalised' input passed to the servo motor

        Returns:
            int: the corresponding value to be written by wiringpi

        """
        return int(pwm_input * wiringpi_wrapper.pwm_pin.pwm_range)

    # noinspection PyMethodMayBeStatic
    def stop_pwm(self):
        """Note that the servo motor will still remain engaged after the pi ceases to send a pwm signal."""
        wiringpi_wrapper.write_pwm_to_pin_18(0)


def _wait_until(wake_up_time):
    while time.time() < wake_up_time:
        pass
