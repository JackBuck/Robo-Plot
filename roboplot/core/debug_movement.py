"""
Debug Movement Module

This module creates a debug images showing the movement of the plotter.

"""
import os

import cv2
import numpy as np

import roboplot.config as config


class Colour:
    Yellow = (0, 255, 255)
    Pink = (127, 0, 255)
    Light_Blue = (240, 240, 0)
    Purple = (255, 51, 153)


class DebugImage:
    def __init__(self, millimetres_per_step, bgimage_path=None):
        """
        Creates debug image.

        Args:
            millimetres_per_step (float): The number of millimetres per step (used to compute the number of steps per
                                          save)
            bgimage_path (str): An optional path to a background image to use for the debugger output.

        """

        self.dir_path = os.path.join(config.resources_dir, 'DebugImages')

        # Create the directory if it doesn't exist
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path, 0o750)  # drwxr-x---

        # Remove any existing debug files from folder
        file_list = os.listdir(self.dir_path)
        for file_name in file_list:
            os.remove(self.dir_path + "/" + file_name)

        # Background image
        if bgimage_path is not None:
            self.debug_image = cv2.imread(bgimage_path)
            cv2.resize(self.debug_image, (594, 420))
        else:
            self.debug_image = np.zeros((594, 420, 3), np.uint8)

        # This value should depend on the picture size chosen currently a 1:1 mappings
        self.pixels_per_mm = 2

        # Choose how often an image is saved.
        self.millimeters_between_saves = 20
        self.steps_between_saves = self.millimeters_between_saves / millimetres_per_step

        cv2.imwrite(os.path.join(self.dir_path, 'Initial_Image.png'), self.debug_image)

        self.steps_since_save = 0
        self.image_index = 0
        self.colour_index = 0
        self.colour = Colour.Yellow

    def add_point(self, point):
        """
        This function adds the locations to a buffer and periodically adds them to the image and displays the result.

        Args:
            point: Point to be added to the buffer (in mm)
        """

        pixel = (int(round(point[0] * self.pixels_per_mm)), int(round(point[1] * self.pixels_per_mm)))

        if pixel[0] >= 0 and pixel[1] >= 0:
            self.debug_image[pixel] = self.colour

        self.steps_since_save += 1

        # If the buffer is sufficiently large save/display the image.
        if self.steps_since_save > self.steps_between_saves:
            self.save_image()

    def change_colour(self):
        """This function changes the colour of the pixels being added to the image."""

        scan = [Colour.Yellow, Colour.Pink, Colour.Light_Blue, Colour.Purple]

        self.colour_index = (self.colour_index + 1) % len(scan)
        self.colour = scan[self.colour_index]

    def save_image(self):
        cv2.imwrite(os.path.join(self.dir_path, "Debug_Image" + str(self.image_index) + ".png"), self.debug_image)
        self.image_index += 1
        self.steps_since_save = 0
