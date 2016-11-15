from Motor import Motor

# Define the sequence and pins of the motor
sequence = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]
pins = [17, 22, 23, 24]

# Create motor instance
a_motor = Motor(pins, sequence, 10.0)

# Start motor for 60s
a_motor.Start(60)
