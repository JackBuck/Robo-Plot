import numpy as np

import roboplot.core.curves as curves
import roboplot.core.debug_movement as debug_movement
import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.stepper_control as stepper_control
from roboplot.core.camera.camera_wrapper import Camera


class Plotter:
    default_pen_speed = np.inf  # I.e. as fast as possible
    default_resolution = 0.1

    def __init__(self,
                 axes: stepper_control.AxisPair,
                 pen: liftable_pen.LiftablePen,
                 camera: Camera,
                 pen_to_camera_offset):
        """
        Create a Plotter.

        Args:
            axes (stepper_control.AxisPair): the axes
            pen (liftable_pen.LiftablePen): the pen
            camera (Camera): the camera
            pen_to_camera_offset (iterable): the offset (y,x) of the camera from the pen
        """
        self._axes = axes
        self._pen = pen
        self._camera = camera
        self._pen_to_camera_offset = pen_to_camera_offset

    def home(self):
        self._pen.lift()
        self._axes.home()

    def draw(self, curve_list, pen_speed: float = default_pen_speed, resolution: float = default_resolution) -> None:
        """
        Algorithm:
         - Lift the pen
         - Move to the start
         - Drop the pen
         - Draw all the curves
         - Lift the pen

        Args:
            curve_list: the curves to be drawn
            pen_speed: the speed of the pen (mm/s)
            resolution: the length of the line segments in which to split the curves before drawing
        """

        if isinstance(curve_list, curves.Curve):
            curve_list = [curve_list]

        self._lift_pen()
        if len(curve_list) > 0:
            self._move_to_start_of_curve(curve_list[0], pen_speed, resolution)
            self._drop_pen()
            for curve in curve_list:
                self._axes.follow(curve, pen_speed, resolution)
            self._lift_pen()

    def follow_with_camera(self, curve_list, camera_speed: float = default_pen_speed, resolution: float = default_resolution):
        offset_curves = [c.offset(-self._pen_to_camera_offset) for c in curve_list]
        self.follow_with_pen(offset_curves, pen_speed=camera_speed, resolution=resolution)

    def follow_with_pen(self, curve_list, pen_speed: float = default_pen_speed, resolution: float = default_resolution):
        """
        Algorithm:
          - Lift the pen
          - Follow all the curves

        Args:
            curve_list: the curves to be drawn
            pen_speed: the speed of the pen (mm/s)
            resolution: the length of the line segments in which to split the curves before following
        """
        # TODO: It is not ideal to not be changing colour each curve when the pen is up...
        if isinstance(curve_list, curves.Curve):
            curve_list = [curve_list]

        self._lift_pen()
        for curve in curve_list:
            self._axes.follow(curve, pen_speed, resolution)

    def move_camera_to(self, target_location, camera_speed: float = default_pen_speed) -> None:
        """
        Move the camera from the current location to the target location.

        Args:
            target_location: the target location
            camera_speed: the camera speed (mm/s) (optional)
        """
        self.move_pen_to(target_location - self._pen_to_camera_offset, pen_speed=camera_speed)

    def move_pen_to(self, target_location, pen_speed: float = default_pen_speed) -> None:
        """
        Move the pen from the current location to the target location.

        Args:
            target_location: the target location
            pen_speed: the pen speed (mm/s) (optional)
        """
        self._lift_pen()
        self._axes.move_to(target_location, pen_speed)

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
