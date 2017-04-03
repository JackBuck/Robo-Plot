"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import os
import datetime

import cv2
import numpy as np
import picamera
import picamera.array

import roboplot.config as config


class Camera:
    _photo_index = 0

    def take_photo_at(self, camera_centre):
        with picamera.PiCamera() as camera:
            camera.resolution = config.CAMERA_RESOLUTION
            camera.framerate = 24
            with picamera.array.PiRGBArray(camera) as output:
                camera.capture(output, 'bgr', use_video_port=True)
                outputarray = output.array

            # Rotate image to oriented it with paper.
            outputarray = np.rot90(outputarray, 3)

            # Save photo.
            filename = datetime.datetime.now().strftime("%M%S.%f_") + \
                       str(camera_centre[0]) \
                       + '_' \
                       + str(camera_centre[1]) + '_Photo_' + str(self._photo_index) + '.jpg'

            cv2.imwrite(os.path.join(config.debug_output_folder, filename), outputarray)
            self._photo_index += 1

            return outputarray

    @property
    def resolution_mm_xy(self):
        """The size of a photo (width, height) in mm"""
        return self.resolution_pixels_xy * self.pixels_to_mm_scale_factors_xy

    @property
    def resolution_pixels_xy(self):
        """The size of a photo in pixels"""
        return np.array(config.CAMERA_RESOLUTION)

    @property
    def pixels_to_mm_scale_factors_xy(self):
        return np.array([config.X_PIXELS_TO_MILLIMETRE_SCALE, config.Y_PIXELS_TO_MILLIMETRE_SCALE])
