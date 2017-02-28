import roboplot.core.servo_motor as servo_motor


class LiftablePen:
    def __init__(self, servo: servo_motor.ServoMotor, position_when_down: float, position_when_up: float):
        assert servo.input_is_in_range(position_when_down)
        assert servo.input_is_in_range(position_when_up)

        self._servo = servo
        self._position_when_down = position_when_down
        self._position_when_up = position_when_up

    def lift(self):
        self._servo.set_position(self._position_when_up)

    def drop(self):
        # TODO: Lower the pen gradually?
        self._servo.set_position(self._position_when_down)
