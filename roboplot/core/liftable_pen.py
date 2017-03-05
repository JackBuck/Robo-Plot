import roboplot.core.servo_motor as servo_motor


class LiftablePen:

    def __init__(self, servo: servo_motor.ServoMotor, position_when_down: float, position_when_up: float,
                 seconds_to_change_position: float = 0.25):
        assert servo.input_is_in_range(position_when_down)
        assert servo.input_is_in_range(position_when_up)

        self._servo = servo
        self._position_when_down = position_when_down
        self._position_when_up = position_when_up
        self._seconds_to_change_position = seconds_to_change_position

    def lift(self):
        self._servo.move_smoothly_to(self._position_when_up, self._seconds_to_change_position)

    def drop(self):
        self._servo.move_smoothly_to(self._position_when_down, self._seconds_to_change_position)
