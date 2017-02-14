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
    steps_since_save = 0
    image_index = 0
    colour_index = 0
    colour = Colour.Yellow

    def __init__(self, millimetres_per_step, bgimage_path=None, pixels_per_mm=2):
        """
        Creates debug image.

        Args:
            millimetres_per_step (float): The number of millimetres per step (used to compute the number of steps per
                                          save)
            bgimage_path (str): An optional path to a background image to use for the debugger output.
            pixels_per_mm (float): This value should depend on the picture size chosen currently a 1:1 mappings

        """

        self.dir_path = os.path.join(config.resources_dir, 'DebugImages')

        # Create the directory if it doesn't exist
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path, 0o750)  # drwxr-x---

        # Remove any existing debug files from folder
        file_list = [f for f in os.listdir(self.dir_path) if os.path.isfile(f)]
        for file_name in file_list:
            os.remove(self.dir_path + "/" + file_name)

        # Setup image dimensions
        self.pixels_per_mm = pixels_per_mm
        a4paper = (297, 210)
        self._image_dimensions_pixels = tuple(int(round(i * self.pixels_per_mm)) for i in a4paper)

        # Background image
        if bgimage_path is not None:
            self.debug_image = cv2.imread(bgimage_path)
            cv2.resize(self.debug_image, self._image_dimensions_pixels)
        else:
            self.debug_image = np.zeros(self._image_dimensions_pixels + (3,), np.uint8)

        # Choose how often an image is saved.
        self.millimeters_between_saves = 20
        self.steps_between_saves = self.millimeters_between_saves / millimetres_per_step

        self.save_image()

    def add_point(self, point):
        """
        This function adds the locations to a buffer and periodically adds them to the image and displays the result.

        Args:
            point: Point to be added to the buffer (in mm)
        """

        pixel = (int(round(point[0] * self.pixels_per_mm)), int(round(point[1] * self.pixels_per_mm)))

        if 0 <= pixel[0] < self._image_dimensions_pixels[0] and \
           0 <= pixel[1] < self._image_dimensions_pixels[1]:
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
        cv2.imwrite(os.path.join(self.dir_path, "DebugImage_{i:04}.jpg".format(i=self.image_index)), self.debug_image)
        self.image_index += 1
        self.steps_since_save = 0
