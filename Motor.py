# Author: Hannah Howell
# Date: 10/11/16

from EmulatorGUI import GPIO
#import RPi.GPIO as GPIO
# This class is the collection of functions to set up and use a motor.
class Motor:
#Initialiser
    def __init__(self, pins, sequence, rps):
        self.GPIO_pins = pins
        self.rps = rps
        self.sequence = sequence
        self.Clockwise = True
        self.waitTime = 200/rps
        self.next_step = 0

        #Setup pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)


# This function steps the motor once and increments the sequence.
    def step(self):
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
        if (self.Clockwise):
            self.next_step = (self.next_step + 1) % 4
        else:
            self.next_step = (self.next_step - 1) % 4


    # This function starts the motor running at the stored rps and direction of the motor
    # for the specified amount of time (in seconds).
    def start(self, time):
        number_of_steps = time/(self.rps*200)

        # Step the motor the required number of steps. Waiting between the steps to achieve
        # required rps
        for step in range(0, number_of_steps):
            self.step()
            time.sleep(self.waitTime)


    # This function changes the direction the motor will move in the next time it steps.
    # This function is simple and is not currently tested.
    def change_direction(self, clockwise):
        self.Clockwise = clockwise




    def __str__(self):
        buf = "Motor.py: Pins:" + str(self.pin[0]) + str(self.pins[2]) + str(self.pins[3]) + str(self.pins[4])
        return buf


