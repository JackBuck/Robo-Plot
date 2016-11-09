# Import libraries
import sys
import time
import RPi.GPIO as GPIO

# Using GPIO references instead of pins
GPIO.setmode(GPIO.BCM)

# Defining GPIO signals
# GPIO17,GPIO22,GPIO23,GPIO24
StepPins = [17, 22, 23, 24]
StepPins2 = [4, 14, 15, 27]

# Set all pins as output
for pin in StepPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)  # keeps it off
for pin in StepPins2:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# sequence
Seq = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]] # For large stepper motors
# Seq2 = [[0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1], [1, 1, 0, 0]] # For small stepper motors

StepCount = len(Seq)  # max length of sequence
StepDir = 1  # Set to 1 or 2 for clockwise; Set to -1 or -2 for anti-clockwise

WaitTime = 1 / 1000

# Initialise variables
StepCounter = 0  # so it will start at the first item in the list

# Start main loop
for number in range(int(sys.argv[1])):  # how many times you want to loop

    for pin in range(0, 4):  # creates an index so goes to 0-3
        xpin = StepPins[pin]
        ypin = StepPins2[pin]

        if Seq[StepCounter][pin] != 0:  # if it is 1 so turn on the pin
            GPIO.output(xpin, True)
            GPIO.output(ypin, True)
        else:  # if it is 0 keep it off
            GPIO.output(xpin, False)
            GPIO.output(ypin, False)

    StepCounter += StepDir  # moves along one in sequence

    # If we reach the end of the sequence
    # start again
    if StepCounter >= StepCount:
        StepCounter = 0
    if StepCounter < 0:
        StepCounter = StepCount + StepDir

    # Wait before moving on
    time.sleep(WaitTime)

GPIO.cleanup()
