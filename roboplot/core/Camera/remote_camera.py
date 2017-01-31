"""
Camera Control Module

This module controls the REMOTE camera for the plotter.

All distances in the module are expressed in MILLIMETRES.

"""
import time
import cv2
import numpy as np
import roboplot.core.Camera.camera_client as camera_client


class RemoteCamera:
    def __init__(self):

        self._dir_path = '../resources/DebugImages/'

    def take_photo(self, camera_centre):

            output = camera_client.take_remote_photo()
            output = output.reshape((112, 128, 3))
            output = output[:200, :200, :]

            # Save photo.
            cv2.imshow(self._dir_path + "Photo:" + self._photo_index + ".jpg", output)
            self._photo_index += 1

            return output


