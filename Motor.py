from EmulatorGUI import GPIO
#import RPi.GPIO as GPIO
# This class is the collection of functions to set up and use a motor.
class Motor:

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

    def step(self):
        for pin in range(0, 4):  # Creates an Index from 0-3
            current_pin = self.GPIO_pins[pin]

            if self.sequence[self.next_step][pin] == 1:
                # Keep/Turn on the pin
                GPIO.output(current_pin, True)
            else:
                # Keep/Turn off the pin off
                GPIO.output(current_pin, False)

        if (self.Clockwise):
            self.next_step = (self.next_step + 1) % 4
        else:
            self.next_step = (self.next_step - 1) % 4



    def start(self, time):

        while(True):
            self.step()

            time.sleep(self.waitTime)
            self.next_step = 0


    def __str__(self):
        buf = "Motor.py: Pins:" + str(self.pin[0]) + str(self.pins[2]) + str(self.pins[3]) + str(self.pins[4])
        return buf


