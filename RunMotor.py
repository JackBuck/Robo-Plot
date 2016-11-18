import Motors
import sys

a_motor = Motors.large_stepper_motor(gpio_pins=[17, 22, 23, 24])
#a_motor.start(duration=60, rps=0.01)

#a_motor.start_distance(sys.argv[1], sys.argv[2], sys.argv[3],sys.argv[4])
a_motor.start_distance(1000, 200, 10, -10)