"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import cv2
import numpy as np
from picamera import PiCamera


class Camera:
    def __init__(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (200, 200)
            camera.framerate = 24

        self._dir_path = '../resources/DebugImages/'

    def take_photo(self, camera_centre):
        with picamera.PiCamera() as camera:
            output = np.empty((112 * 128 * 3,), dtype=np.uint8)
            camera.capture(output, 'bgr', use_video_port=True)
            output = output.reshape((112, 128, 3))
            output = output[:200, :200, :]

            # Save photo.
            cv2.imshow(self._dir_path + "Photo:" + self._photo_index + ".jpg", output)
            self._photo_index += 1

            return output

