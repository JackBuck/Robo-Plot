from roboplot import Motors

a_motor = Motors.large_stepper_motor(gpio_pins=[17, 22, 23, 24])
a_motor.start(duration=60, rps=0.01)
