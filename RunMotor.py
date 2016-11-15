from Motor import Motor

# Define the sequence and pins of the motor
sequence = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]
pins = [17, 22, 23, 24]
steps_per_revolution = 200

# Create motor instance
a_motor = Motor(pins, sequence, steps_per_revolution)

# Start motor for 60s
a_motor.Start(time=60, rps=10)
