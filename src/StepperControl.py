# Import libraries
import sys
import time
import RPi.GPIO as GPIO

# Using GPIO references instead of pins
GPIO.setmode(GPIO.BCM)

# Defining GPIO signals
# Pins 11,15,16,18
# GPIO17,GPIO22,GPIO23,GPIO24
step_pins = [17, 22, 23, 24]
step_pins_2 = [4, 14, 15, 27]

# Set all pins as output
for pin in step_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)  # keeps it off
for pin in step_pins_2:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# sequence
seq = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]  # For large stepper motors
# seq_2 = [[0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1], [1, 1, 0, 0]] # For small stepper motors

# max length of sequence
step_dir = 1  # Set to 1 or 2 for clockwise; Set to -1 or -2 for anti-clockwise

# Initialise variables
wait_time = 10 / 1000  # default wait time change it in code so its easier.
num_rotations_1 = int(sys.argv[1])  # number of loops around the sequence wanted for motor 1 and 2
num_rotations_2 = int(sys.argv[2])

step_counter_1 = 0  # so it will start at the first item in the list. Holds the postion of which list its using in seq or seq_2
step_counter_2 = 0
loop_control = True
rotation_holder_1 = 0  # to represent how many loops of the sequence have been completed so far.
rotation_holder_2 = 0

while loop_control:  # sets up an infinite loop, to be broken when a condition is met later.
    if rotation_holder_1 < num_rotations_1:  # if haven't completed the full sequence specified in args.
        for pin in range(0, 4):  # turn each pin on or off for one of the sub lists.
            xpin = step_pins[pin]

            if seq[step_counter_1][pin] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
            step_counter_1 += step_dir  # increment stepCounter1 to move one along in list of lists.

        if step_counter_1 >= len(seq):  # If the four lists have been runtrough. reset counter. increment rotation holder to show one complete rotation of seq completed.
            step_counter_1 = 0
            rotation_holder_1 += 1

    if rotation_holder_2 < num_rotations_2:  # as above but for second motor
        for pin in range(0, 4):
            ypin = step_pins_2[pin]

            if seq[step_counter_2][pin] != 0:
                GPIO.output(ypin, True)
            else:
                GPIO.output(ypin, False)
            step_counter_2 += step_dir

        if step_counter_2 >= len(seq):
            step_counter_2 = 0
            rotation_holder_2 += 1

    if (rotation_holder_1 >= num_rotations_1) and (rotation_holder_2 >= num_rotations_2):
        # if both motors have completed their specified amount of rotations in args. Stop
        loop_control = False
    else:
        time.sleep(wait_time)  # else wait and continue
