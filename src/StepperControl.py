import sys
import Motors

first_motor = Motors.large_stepper_motor([17, 22, 23, 24])
second_motor = Motors.large_stepper_motor([4, 14, 15, 27])

first_motor_target_steps = int(sys.argv[1]) * first_motor.steps_per_revolution
second_motor_target_steps = int(sys.argv[2]) * second_motor.steps_per_revolution

step_counter_1 = 0
step_counter_2 = 0

more_steps_required = True
while more_steps_required:
    if step_counter_1 < first_motor_target_steps:
        first_motor.step()
        step_counter_1 += 1

    if step_counter_2 < second_motor_target_steps:
        second_motor.step()

    if (step_counter_1 >= first_motor_target_steps) and (step_counter_2 >= second_motor_target_steps):
        more_steps_required = False
