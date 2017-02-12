"""
Debug Movement Module

This module creates a debug images showing the movement of the plotter.

"""
import time
import os
import cv2
import numpy as np
import enum


class Colour:
    Yellow = (0, 255, 255)
    Pink = (127, 0, 255)
    Light_Blue = (240, 240, 0)
    Purple = (255, 51, 153)


class DebugImage:
    def __init__(self, millimetres_per_step):
        """
        Creates debug image.
        """

        self.dir_path = '../resources/Debug_Images/'
        temp = os.getcwd()

        # Remove any existing debug files from folder
        file_list = os.listdir(self.dir_path)
        for file_name in file_list:
            os.remove(self.dir_path + "/" + file_name)

        # Choose whether to start with blank image or background.
        # Blank image
        #self.debug_image = np.zeros((420,594, 3), np.uint8)

        # Background image that can be changed.

        file_path = '../resources/Challenge_2_Test_Images/HackspacePath_Sample3.png'
        self.debug_image = cv2.imread(file_path)

        if self.debug_image is None:
            self.debug_image = np.zeros((420, 594, 3), np.uint8)
        else:
            self.debug_image = cv2.resize(self.debug_image, (420, 594))

        # This value should depend on the picture size chosen
        self.pixels_per_mm = 2

        # Choose how often an image is saved.
        self.millimeters_between_saves = 20
        self.steps_between_saves = self.millimeters_between_saves / millimetres_per_step

        cv2.imwrite(self.dir_path + 'Initial_Image.png', self.debug_image)

        self.steps_since_save = 0
        self.image_index = 0
        self.colour_index = 0
        self.colour = Colour.Yellow

    def add_point(self, point):
        """
        This function adds the locations to a buffer and periodically adds them to the image and displays the result.
        :param point: Point to be added
        :return:
        """

        pixel = (self.debug_image.shape[0] - int(round(point[0])*self.pixels_per_mm) - 1,
                  int(round(point[1]*self.pixels_per_mm)))

        if pixel[0] >= 0 and pixel[1] >= 0:
            self.debug_image[pixel] = self.colour

        self.steps_since_save += 1

        # If the buffer is sufficiently large save/display the image.
        if self.steps_since_save > self.steps_between_saves:
            cv2.imwrite(self.dir_path + "Movement_Debug" + str(self.image_index) + ".jpg", self.debug_image)
            self.image_index += 1
            self.steps_since_save = 0

    def change_colour(self):
        """
        This function changes the colour of the pixels being added to the image.
        :return:
        """

        scan = [Colour.Yellow, Colour.Pink, Colour.Light_Blue, Colour.Purple]

        self.colour_index = (self.colour_index + 1) % len(scan)
        self.colour = scan[self.colour_index]

    def save_image(self):
        cv2.imwrite(self.dir_path + "Movement_Debug" + str(self.image_index) + ".jpg", self.debug_image)
        self.image_index += 1
        self.steps_since_save = 0
