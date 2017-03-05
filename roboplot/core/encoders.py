"""
This module defines a class to manage encoder activities.

Author: Luke W (refactored by Jack)
"""

import time
import threading
import warnings

from roboplot.core.gpio.gpio_wrapper import GPIO
from roboplot.core.stepper_motors import StepperMotor


class Encoder(threading.Thread):
    """
    This class is a collection of functions and variables to setup and use an encoder.

    The encoder loop runs on its own thread, with a small sleep.

    **update_events (set):** Clients wishing to synchronise with the encoder's thread should add a threading.Event()
                             to this container. All events in update_events are 'set' at the end of the encoder loop. It
                             is up to the client to 'clear' them when appropriate.
    """

    state_sequence = ((0, 1), (0, 0), (1, 0), (1, 1))

    _lock = threading.Lock()
    _count = 0
    _exit_requested = False
    _total_number_of_double_steps = 0

    update_events = set()  # Add threading.Event() objects to be 'set' at the end of each iteration of the encoder loop

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
        """Resets the revolutions to 0."""
        with self._lock:
            self._count = 0

    def exit_thread(self):
        """Shortly after calling this function the thread will exit."""
        with self._lock:
            self._exit_requested = True  # TODO: Is there any point in locking here? We do not lock when we read it...

    def _encoder_loop(self) -> None:
        """Loop to update the encoder count until an exit is requested."""

        current_section = self._compute_current_section()

        # Infinite while loop until program ends, at which point a flag can be set from another thread
        while not self._exit_requested:
            # Compute which of the four possible states the encoder is in
            previous_section = current_section
            current_section = self._compute_current_section()

            # Sections are modulo 4; hopefully the change is 0,1, or -1 modulo 4
            count_change = _get_modular_representative(current_section - previous_section, min=-1, modulus=4)

            # But if it is not...
            if count_change == 2:
                self._total_number_of_double_steps += 1
                warnings.warn("Encoder on thread {} moved more than one step ({})".format(
                    self.name, self._total_number_of_double_steps))
                count_change = 0  # We do not know whether we gained two or lost two steps - so do nothing!

            # Use a lock to make count variable thread safe
            if count_change != 0:
                with self._lock:
                    self._count += count_change

            # Signal to waiters that we have just updated
            for update_event in self.update_events:
                update_event.set()

            time.sleep(0.001)  # If we do not sleep, then the encoder will hog the cpu

    def _compute_current_section(self):
        """Returns a number modulo 4 to indicate the current reading from the encoder."""
        a = GPIO.input(self.a_pin)
        b = GPIO.input(self.b_pin)
        return self.state_sequence.index((a, b))


def _get_modular_representative(value, min, modulus):
    return ((value - min) % modulus) + min


class StepperEncoderBinding:
    """
    Augments the step() method on a stepper motor with the ability to change the GPIO pins read by an encoder when
    stepping.

    This class is intended for use with simulated hardware.
    """
    _non_resettable_encoder_count = 0
    _non_resettable_motor_step_count = 0

    def __init__(self, encoder: Encoder, stepper: StepperMotor):
        # Pull info out of encoder
        self._encoder_pin_a = encoder.a_pin
        self._encoder_pin_b = encoder.b_pin
        self._encoder_resolution = encoder.resolution
        if encoder.invert_revolutions:
            self._encoder_state_sequence = tuple(reversed(encoder.state_sequence))
        else:
            self._encoder_state_sequence = encoder.state_sequence
        self._encoder_state_index = self._encoder_state_sequence.index((GPIO.input(self._encoder_pin_a),
                                                                        GPIO.input(self._encoder_pin_b)))

        # Pull info out of stepper
        self._stepper = stepper

        # Patch the method on the stepper
        self._append_to_motor_step_method(self._addition_to_motor_step_method)

    def _append_to_motor_step_method(self, additional_method):
        old_method = self._stepper.step

        def new_step_method():
            old_method()
            additional_method()

        self._stepper.step = new_step_method

    def _addition_to_motor_step_method(self):
        encoder_steps = 0
        if self._stepper.clockwise:
            self._non_resettable_motor_step_count += 1
            while self._motor_revolutions > self._encoder_revolutions + self._encoder_resolution:
                encoder_steps += 1
                self._step_encoder_forwards()
        else:
            self._non_resettable_motor_step_count -= 1
            while self._motor_revolutions < self._encoder_revolutions - self._encoder_resolution:
                encoder_steps += 1
                self._step_encoder_backwards()

    @property
    def _motor_revolutions(self):
        return self._non_resettable_motor_step_count / self._stepper.steps_per_revolution

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
