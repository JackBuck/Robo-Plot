"""
Debug Movement Module

This module creates a debug images showing the movement of the plotter.

"""
import os
import queue
import threading
import warnings

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
    colour = Colour.Pink
    override_colour = None  # If not none, then this colour will be used instead of the 'colour' attribute

    def __init__(self, millimetres_per_step, bgimage_path=None, pixels_per_mm=3):
        """
        Creates debug image.

        Args:
            millimetres_per_step (float): The number of millimetres per step (used to compute the number of steps per
                                          save)
            bgimage_path (str): An optional path to a background image to use for the debugger output.
            pixels_per_mm (float): This value should depend on the picture size chosen currently a 1:1 mappings

        """

        # Create the directory if it doesn't exist
        if not os.path.exists(config.debug_output_folder):
            os.mkdir(config.debug_output_folder, 0o750)  # drwxr-x---

        # Remove any existing debug files from folder
        file_list = [f for f in os.listdir(config.debug_output_folder) if os.path.isfile(os.path.join(config.debug_output_folder, f))]
        for file_name in file_list:
            os.remove(config.debug_output_folder + "/" + file_name)

        # Setup image dimensions
        self.pixels_per_mm = pixels_per_mm
        a4paper_with_border = (315, 445.5)  # openCV asks for image dimensions as width then height.

        self._image_dimensions_pixels = tuple(int(round(i * self.pixels_per_mm)) for i in a4paper_with_border)

        # Background image
        if bgimage_path is not None:
            self.debug_image = cv2.imread(bgimage_path)
        else:
            self.debug_image = np.zeros(self._image_dimensions_pixels + (3,), np.uint8)

        self.debug_image = cv2.resize(self.debug_image, self._image_dimensions_pixels)

        # Choose how often an image is saved.
        self.millimeters_between_saves = 20
        self.steps_between_saves = self.millimeters_between_saves / millimetres_per_step

        # Initialise the image saver, and save the first image
        self._image_saver = ThreadedImageSaver()
        self.save_image()

    def add_point(self, point):
        """
        This function adds the locations to a buffer and periodically adds them to the image and displays the result.

        Args:
            point: Point to be added to the buffer (in mm)
        """

        pixel = tuple(int(round(i * self.pixels_per_mm)) for i in point)

        # The point is (y, x) and the shape is width height.
        if 0 <= pixel[0] < self._image_dimensions_pixels[1] and \
           0 <= pixel[1] < self._image_dimensions_pixels[0]:
            self.debug_image[pixel] = self.override_colour or self.colour
           # print(' Pixel: ' + str(pixel))
        else:
            warnings.warn('Tried to populate pixel out of image bounds.')


        self.steps_since_save += 1

        # If the buffer is sufficiently large save/display the image.
        if self.steps_since_save > self.steps_between_saves:
            self.save_image()

    def change_colour(self):
        """
        This function changes the colour of the pixels being added to the image to one of the colours designated
        for pen-down drawing.
        """

        scan = [Colour.Pink, Colour.Light_Blue, Colour.Purple]

        self.colour_index = (self.colour_index + 1) % len(scan)
        self.colour = scan[self.colour_index]

    def save_image(self):
        savepath = os.path.join(config.debug_output_folder, "DebugImage_{i:04}.jpg".format(i=self.image_index))

        # Threaded in the hope that we can reduce time wasted waiting on IO
        debug_image_copy = self.debug_image.copy()
        self._image_saver.save_image(img=debug_image_copy, savepath=savepath)

        #self.image_index += 1
        self.steps_since_save = 0


class ThreadedImageSaver:
    """
    A class which manages the saving of images on a different thread.

    When the queue is empty, the worker thread dies.
    This means that we do not need to signal to the ThreadedImageSaver that there will be no more images when we
    wish to end the program.

    If the worker thread is dead when a new request to save an image is received, the image saver will restart the
    worker thread.
    """

    def __init__(self):
        self._image_queue = queue.Queue()
        self._worker_thread = None  # type: threading.Thread

    def save_image(self, img: np.ndarray, savepath: str) -> None:
        """
        Queue an image to be saved.

        Args:
            img (np.ndarray): The image to be saved. This is not copied, so if you wish to modify the image after
                              saving it, then copy it first!
            savepath (str): The file path at which to save the image.
        """
        self._image_queue.put({'image': img, 'savepath': savepath})
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._restart_image_saver()

    def _restart_image_saver(self):
        self._worker_thread = threading.Thread(target=self._image_saver_loop)
        self._worker_thread.start()

    def _image_saver_loop(self):
        while True:
            try:
                item = self._image_queue.get(block=False)
            except queue.Empty:
                break

            cv2.imwrite(item['savepath'], item['image'])
            self._image_queue.task_done()
