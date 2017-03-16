"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import os
import time

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

        outputarray = np.rot90(outputarray, 1)
        cv2.imshow('Rotate1', outputarray)
        outputarray = np.rot90(outputarray, 2)
        cv2.imshow('Rotate2', outputarray)
        outputarray = np.rot90(outputarray, 3)
        cv2.imshow('Rotate3', outputarray)

        # Save photo.
        cv2.imwrite(os.path.join(config.debug_output_folder, "Photo_" + str(self._photo_index) + ".jpg"),
                    outputarray)
        self._photo_index += 1

        return outputarray
