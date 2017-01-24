"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import config
import cv2
import numpy as np
import dummy_camera0
from picamera import PiCamera

class Camera:
    def __init__(self):

    def take_photo(self, camera_centre):
        with picamera.PiCamera() as camera:
            camera.resolution = (200, 200)
            camera.framerate = 24
            output = np.empty((112 * 128 * 3,), dtype=np.uint8)
            camera.capture(output, 'bgr', use_video_port=True)
            output = output.reshape((112, 128, 3))
            output = output[:200, :200, :]
            return output


