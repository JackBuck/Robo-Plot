"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import cv2
import numpy as np
import picamera
import picamera.array

class Camera:
    def __init__(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (200, 200)
            camera.framerate = 24

        self._photo_index = 0

    def take_photo_at(self, camera_centre):
        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as output: 
                camera.capture(output, 'bgr', use_video_port=True)
                outputarray = output.array

            # Save photo.
            cv2.imwrite(config.debug_output_folder + "Photo:" + str(self._photo_index) + ".jpg", outputarray)
            self._photo_index += 1

            return outputarray
