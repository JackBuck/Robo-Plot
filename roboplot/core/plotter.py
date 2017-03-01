import roboplot.core.curves as curves
import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.stepper_control as stepper_control


class Plotter:
    default_pen_speed = 100  # I.e. as fast as possible
    default_resolution = 0.1

    def __init__(self, axes: stepper_control.AxisPair, pen: liftable_pen.LiftablePen):
        self._axes = axes
        self._pen = pen

    def draw(self, curve: curves.Curve, pen_speed: float = default_pen_speed, resolution=default_resolution):
        self._pen.lift()
        self._move_to_start_of_curve(curve, pen_speed, resolution)
        self._pen.drop()
        self._axes.follow(curve, pen_speed, resolution)
        self._pen.lift()

    def _move_to_start_of_curve(self, curve, pen_speed, resolution):
        self._axes.follow(
            curve=curves.LineSegment(self._axes.current_location, curve.evaluate_at(0)),
            pen_speed=pen_speed,
            resolution=resolution)
