import numpy as np

import roboplot.config as config
import roboplot.core.curves as curves
import roboplot.core.debug_movement as debug_movement
import roboplot.core.liftable_pen as liftable_pen
import roboplot.core.stepper_control as stepper_control
from roboplot.core.camera.camera_wrapper import Camera
import roboplot.core.camera.camera_utils as camera_utils


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
        self._pen_to_camera_offset = np.array(pen_to_camera_offset)

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
        if isinstance(curve_list, curves.Curve):
            curve_list = [curve_list]

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

    def take_photo_at(self, target_photo_centre):
        current_camera_location = self._axes.current_location + config.CAMERA_OFFSET

        #TODO if overstep is fixed this fudge can be removed.
        is_at_centre = abs(current_camera_location[0] - target_photo_centre[0]) < 0.05 and \
                       abs(current_camera_location[1] - target_photo_centre[1]) < 0.05

        if not is_at_centre:
            photo = self._camera.take_photo_at(self._axes.current_location + config.CAMERA_OFFSET)

            centre_displacement = target_photo_centre - self._axes.current_location
            pixel_centre_displacement = [int(photo.shape[0]/2) + centre_displacement[0] / config.Y_PIXELS_TO_MILLIMETRE_SCALE,
                                         int(photo.shape[1] / 2) +centre_displacement[1] / config.X_PIXELS_TO_MILLIMETRE_SCALE]

            photo = camera_utils.pad_image(photo, pixel_centre_displacement)
        else:
            photo = self._camera.take_photo_at(self._axes.current_location + config.CAMERA_OFFSET)

        return photo

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
        return PlotterWithDebugImage(plotter._axes, plotter._pen, plotter._camera, plotter._pen_to_camera_offset)

    def __init__(self,
                 axes: stepper_control.AxisPairWithDebugImage,
                 pen: liftable_pen.LiftablePen,
                 camera: Camera,
                 pen_to_camera_offset):

        # Setup the axes member to use a debug image
        if not isinstance(axes, stepper_control.AxisPairWithDebugImage):
            axes = stepper_control.AxisPairWithDebugImage.create_from(axes)

        # Initialise
        super().__init__(axes, pen, camera, pen_to_camera_offset)
        self.debug_image = axes.debug_image

    def _lift_pen(self):
        self.debug_image.override_colour = debug_movement.Colour.Yellow
        super()._lift_pen()

    def _drop_pen(self):
        self.debug_image.override_colour = None
        super()._drop_pen()
