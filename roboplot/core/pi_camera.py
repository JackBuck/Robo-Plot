"""
Camera Control Module

This module controls the camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import config
import cv2
import numpy as np
import dummy_camera
#from picamera import PiCamera


def take_photo():
    if use_dummy_photo:
        a_dummy_camera = dummy_camera.DummyCamera()
        output = a_dummy_camera.take_dummy_photo(global_position)
    else:
        y=0
        #with picamera.PiCamera() as camera:
        #    camera.resolution = (200, 200)
        #    camera.framerate = 24
        #    output = np.empty((112 * 128 * 3,), dtype=np.uint8)
        #    camera.capture(output, 'bgr', use_video_port=True)
        #    output = output.reshape((112, 128, 3))
        #    output = output[:100, :100, :]


    if debug:
        cv2.imshow("Photo", output)
        cv2.imwrite("../../resources/Challenge_2_Test_Images")