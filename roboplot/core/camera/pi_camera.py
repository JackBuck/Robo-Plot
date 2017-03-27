"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import os

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
                outputarray = np.rot90(outputarray, 3)

            # Save photo.
            cv2.imwrite(os.path.join(config.debug_output_folder, 'Photo_{:03}.jpg'.format(self._photo_index)),
                        outputarray)
            self._photo_index += 1

            return outputarray

    @property
    def resolution_mm(self):
        """The size of a photo in mm"""
        return self.resolution_pixels * self.pixels_to_mm_scale_factors

    @property
    def resolution_pixels(self):
        """The size of a photo in pixels"""
        return np.array(config.CAMERA_RESOLUTION)

    @property
    def pixels_to_mm_scale_factors(self):
        return np.array([config.Y_PIXELS_TO_MILLIMETRE_SCALE, config.X_PIXELS_TO_MILLIMETRE_SCALE])
