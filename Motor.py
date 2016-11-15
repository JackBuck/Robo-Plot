# Author: Hannah Howell
# Date: 10/11/16

# import RPi.GPIO as GPIO
from EmulatorGUI import GPIO


class Motor:
    """This class is the collection of functions to set up and use a motor."""

    def __init__(self, pins, sequence, rps):
        """Initialiser"""
        self.GPIO_pins = pins
        self.rps = rps
        self.sequence = sequence
        self.clockwise = True
        self.wait_time = 200 / rps
        self.next_step = 0

        # Setup pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def step(self):
        """This function steps the motor once and increments the sequence."""

        for pin in range(0, 4):  # Creates an Index from 0-3

            # Check what status the current pin should be set to based on the current step count.
            current_pin = self.GPIO_pins[pin]

            if self.sequence[self.next_step][pin] == 1:
                # Keep/Turn on the pin
                GPIO.output(current_pin, True)
            else:
                # Keep/Turn off the pin off
                GPIO.output(current_pin, False)

        # Increment / decrement the step count based on the direction of the motor.
        if self.clockwise:
            self.next_step = (self.next_step + 1) % 4
        else:
            self.next_step = (self.next_step - 1) % 4

    def start(self, time):
        """This function starts the motor running at the stored rps and direction of the motor for the specified
        amount of time (in seconds)."""
        number_of_steps = time / (self.rps * 200)

        # Step the motor the required number of steps. Waiting between the steps to achieve
        # required rps
        for step in range(0, number_of_steps):
            self.step()
            time.sleep(self.wait_time)

    def change_direction(self, clockwise):
        """This function changes the direction the motor will move in the next time it steps.
        This function is simple and is not currently tested."""
        self.clockwise = clockwise

    def __str__(self):
        buf = "Motor.py: Pins:" + str(self.pins[0]) + str(self.pins[2]) + str(self.pins[3]) + str(self.pins[4])
        return buf
