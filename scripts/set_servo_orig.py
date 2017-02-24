# Working range is from 0.028 to 0.12

# Note: Command line syntax for this module
# Servo.py 0.5
# Servo.py 0.1
#
# Takes 1 argument which is floating number 0<x<1

# import wiringpi python wrapper
import wiringpi
import sys
import time

# Raspberry PI BCM 18 = only PWM pin (according to the internet)
SERVO = 18
PWM_RANGE = 500
PWM_DIVISOR = 765

# Initialise PWM pin
wiringpi.wiringPiSetupGpio()  # Setup wiringpi
wiringpi.pinMode(SERVO, wiringpi.PWM_OUTPUT)  # Set SERVO pin as PWM output
wiringpi.pwmWrite(SERVO, 0)  # Turn output off

# Setup PWM
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)  # Set PWM mode as mark space (as opposed to balanced - the default)
wiringpi.pwmSetRange(PWM_RANGE)  # Set PWM range (range of duty cycles)
wiringpi.pwmSetClock(PWM_DIVISOR)  # Set PWM clock divisor
# Note: PWM Frequency = 19.2MHz / (PWM_DIVISOR * PWM_RANGE)

# Set output as defined by command line
PWM_OUTPUT = int(float(sys.argv[1]) * PWM_RANGE)
print(PWM_OUTPUT)

# If command line input > 1 then set to maximum
# if command line inptu < 0 then set to minimum
if PWM_OUTPUT > PWM_RANGE:
    PWM_OUTPUT = PWM_RANGE
elif PWM_OUTPUT < 0:
    PWM_OUTPUT = 0

wiringpi.pwmWrite(SERVO, PWM_OUTPUT)

time.sleep(1)
