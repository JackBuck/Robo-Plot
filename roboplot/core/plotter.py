import roboplot.core.curves as curves
import roboplot.core.debug_movement as debug_movement
import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.stepper_control as stepper_control


class Plotter:
    default_pen_speed = 100  # I.e. as fast as possible
    default_resolution = 0.1

    def __init__(self, axes: stepper_control.AxisPair, pen: liftable_pen.LiftablePen):
        self._axes = axes
        self._pen = pen

    def draw(self, curve: curves.Curve, pen_speed: float = default_pen_speed, resolution=default_resolution):
        """Draw the curve, lifting the pen before and after."""
        self._lift_pen()
        self._move_to_start_of_curve(curve, pen_speed, resolution)
        self._drop_pen()
        self._axes.follow(curve, pen_speed, resolution)
        self._lift_pen()

    def _lift_pen(self):
        self._pen.lift()

    def _drop_pen(self):
        self._pen.drop()

    def _move_to_start_of_curve(self, curve, pen_speed, resolution):
        self._axes.follow(
            curve=curves.LineSegment(self._axes.current_location, curve.evaluate_at(0)),
            pen_speed=pen_speed,
            resolution=resolution)


class PlotterWithDebugImage(Plotter):
    @staticmethod
    def create_from(plotter: Plotter):
        return PlotterWithDebugImage(plotter._axes, plotter._pen)

    def __init__(self, axes: stepper_control.AxisPairWithDebugImage, pen: liftable_pen.LiftablePen):
        # Setup the axes member to use a debug image
        if not isinstance(axes, stepper_control.AxisPairWithDebugImage):
            axes = stepper_control.AxisPairWithDebugImage.create_from(axes)

        # Initialise
        super().__init__(axes, pen)
        self.debug_image = axes.debug_image

    def _lift_pen(self):
        self.debug_image.override_colour = debug_movement.Colour.Yellow
        super()._lift_pen()

    def _drop_pen(self):
        self.debug_image.override_colour = None
        super()._drop_pen()
