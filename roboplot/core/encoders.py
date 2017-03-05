"""
This module defines a class to manage encoder activities.

Author: Luke W (refactored by Jack)
"""

import threading
import warnings

from roboplot.core.gpio.gpio_wrapper import GPIO
from roboplot.core.stepper_motors import StepperMotor


class Encoder(threading.Thread):
    """This class is a collection of functions and variables to setup and use an encoder"""

    state_sequence = ((0, 1), (0, 0), (1, 0), (1, 1))

    _lock = threading.Lock()
    _count = 0
    _exit_requested = False
    _total_number_of_double_steps = 0

    def __init__(self, gpio_pins, positions_per_revolution, invert_revolutions=False, thread_name=None):
        """
        Initialises the encoder class.

        Args:
            gpio_pins: BCM number of the GPIO pins which make up the A and B channel of the encoder.
                       See pin allocation scheme on google drive.

            positions_per_revolution (int): the number of counts the encoder has per revolution.

            invert_revolutions (bool): determines which direction is reported as 'increasing' revolutions.

            thread_name (str): a name to use to identify the base class thread object.
        """

        # Initialise thread object (base class initialiser)
        threading.Thread.__init__(self, group=None, target=self._encoder_loop, name=thread_name)

        # In python, class members appear to be created when you refer to them
        self._positions_per_revolution = positions_per_revolution
        self.invert_revolutions = invert_revolutions
        self.a_pin = gpio_pins[0]
        self.b_pin = gpio_pins[1]

        # Setup gpio_pins
        for pin in (self.a_pin, self.b_pin):
            GPIO.setup(pin, GPIO.IN)

    @property
    def resolution(self) -> float:
        """The size of a step on the encoder as a proportion of a revolution."""
        return 1 / self._positions_per_revolution

    @property
    def revolutions(self) -> float:
        """The number of partial revolutions completed since the last reset (or since initialisation)."""
        sign = -1 if self.invert_revolutions else 1
        return sign * self._count / self._positions_per_revolution

    def reset_position(self):
        """
        This function resets the position to 0
        """
        with self._lock:
            self._count = 0

    def exit_thread(self):
        """
        This function sets up the conditions to kill the thread

        Shortly after calling this function the thread will exit
        """
        with self._lock:
            self._exit_requested = True  # TODO: Is there any point in locking here? We do not lock when we read it...

    def _encoder_loop(self):
        """
        Loop to update the encoder count until an exit is requested.

        Returns:
            None
        """

        current_section = self._compute_current_section()

        # Infinite while loop until program ends, at which point a flag can be set from another thread
        while not self._exit_requested:
            previous_section = current_section
            current_section = self._compute_current_section()

            # Sections are modulo 4; hopefully the change is 0,1, or -1 modulo 4
            count_change = _get_modular_representative(current_section - previous_section, min=-1, modulus=4)

            # But if it is not...
            if count_change == 2:
                self._total_number_of_double_steps += 1
                warnings.warn("Encoder moved more than one step ({})".format(self._total_number_of_double_steps))
                count_change = 0  # We do not know whether we gained two or lost two steps - so do nothing!

            # Use a lock to make count variable thread safe
            if count_change != 0:
                with self._lock:
                    self._count += count_change

    def _compute_current_section(self):
        """
        Returns a number modulo 4 to indicate the current reading from the encoder.
        """
        a = GPIO.input(self.a_pin)
        b = GPIO.input(self.b_pin)
        return self.state_sequence.index((a, b))


def _get_modular_representative(value, min, modulus):
    return ((value - min) % modulus) + min


class StepperBoundToEncoder(StepperMotor):
    _non_resettable_encoder_count = 0
    _non_resettable_motor_step_count = 0

    def __init__(self, encoder: Encoder, stepper: StepperMotor):
        super().__init__(stepper._gpio_pins,
                         stepper._sequence,
                         stepper.steps_per_revolution,
                         stepper._minimum_seconds_between_steps)

        self._encoder_pin_a = encoder.a_pin
        self._encoder_pin_b = encoder.b_pin
        self._encoder_resolution = encoder.resolution
        if encoder.invert_revolutions:
            self._encoder_state_sequence = tuple(reversed(encoder.state_sequence))
        else:
            self._encoder_state_sequence = encoder.state_sequence
        self._encoder_state_index = self._encoder_state_sequence.index(GPIO.input(self._encoder_pin_a),
                                                                       GPIO.input(self._encoder_pin_b))

    def step(self):
        super().step()

        if self.clockwise:
            self._non_resettable_motor_step_count += 1
            while self._motor_revolutions > self._encoder_revolutions - self._encoder_resolution:
                self._step_encoder_forwards()
        else:
            self._non_resettable_motor_step_count -= 1
            while self._motor_revolutions < self._encoder_revolutions + self._encoder_resolution:
                self._step_encoder_backwards()

    @property
    def _motor_revolutions(self):
        return self._non_resettable_motor_step_count / self.steps_per_revolution

    @property
    def _encoder_revolutions(self):
        return self._non_resettable_encoder_count * self._encoder_resolution

    def _step_encoder_forwards(self):
        self._encoder_state_index = (self._encoder_state_index + 1) % len(self._encoder_state_sequence)
        self._update_encoder_gpio()
        self._non_resettable_encoder_count += 1

    def _step_encoder_backwards(self):
        self._encoder_state_index = (self._encoder_state_index - 1) % len(self._encoder_state_sequence)
        self._update_encoder_gpio()
        self._non_resettable_encoder_count -= 1

    def _update_encoder_gpio(self):
        target_state = self._encoder_state_sequence[self._encoder_state_index]
        GPIO.cheeky_output(self._encoder_pin_a, target_state[0])
        GPIO.cheeky_output(self._encoder_pin_b, target_state[1])


class PretendEncoder:
    """A wrapper class to give a StepperMotor an Encoder interface."""

    _offset_from_motor = 0

    def __init__(self, motor: StepperMotor):
        """
        Initialises an encoder which wraps a supplied encoder.

        Position measurements are determined by querying the supplied motor.

        This class is intended to be used as a replacement for a real encoder class when testing without real
        hardware. As such,the motor passed to this method is treated as completely 'readonly'.

        Args:
            motor: The stepper motor to wrap as an encoder.
        """
        self._motor = motor

    @property
    def resolution(self) -> float:
        """The size of a step on the encoder as a proportion of a revolution."""
        return 1 / self._motor.steps_per_revolution

    @property
    def revolutions(self):
        """The number of revolutions completed, as measured by the stepper motor."""
        return (self._motor.cumulative_step_count + self._offset_from_motor) / self._motor.steps_per_revolution

    def reset_position(self):
        """Resets the position of the encoder without affecting the count on the wrapped motor."""
        self._offset_from_motor = -self._motor.cumulative_step_count

    # noinspection PyMethodMayBeStatic
    def exit_thread(self):
        """Does nothing"""
        pass

    # noinspection PyMethodMayBeStatic
    def join(self):
        pass
