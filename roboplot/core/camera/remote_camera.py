"""
Camera Control Module

This module controls the REMOTE camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time

import cv2
import numpy as np

import roboplot.core.camera.camera_client as camera_client


class RemoteCamera:
    def __init__(self):

        self._photo_index = 0

    def take_photo_at(self, camera_centre):

            output = camera_client.take_remote_photo()
            output = output[:200, :200, :]

            # Save photo.
            cv2.imwrite(config.debug_output_folder + "Photo:" + str(self._photo_index) + ".jpg", output)
            self._photo_index += 1

            return output


