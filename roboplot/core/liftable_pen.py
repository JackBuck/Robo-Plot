import roboplot.core.servo_motor as servo_motor


class LiftablePen:
    def __init__(self, servo: servo_motor.ServoMotor, degrees_when_down: float, degrees_when_up: float):
        assert servo.angle_is_in_range(degrees_when_down)
        assert servo.angle_is_in_range(degrees_when_up)

        self._servo = servo
        self._degrees_when_down = degrees_when_down
        self._degrees_when_up = degrees_when_up

    def lift(self):
        self._servo.rotate_to(self._degrees_when_up)

    def drop(self):
        self._servo.rotate_to(self._degrees_when_down)
