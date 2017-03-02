# import the necessary packages
import os

import numpy as np
import cv2

import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis


def determine_starting_direction(img):
    """

    Args:
        img: The image whose centre is at the centre of the gree triangle which has now been made
        white.

    Returns:
        enum orientation.
    """

    # Extract centre of the image.

    img_width = img.shape[0]
    img_height = img.shape[1]

    sub_array = img[int(img_width/3):int(2*img_width/3), int(img_height/3):int(2*img_height/3)]

    # Determine which orientation contains the most white pixels.
    # North
    north_sub_array = sub_array[:int(sub_array.shape[0] / 2), :]
    north_num_white_pixels = north_sub_array.sum()

    # East
    east_sub_array = sub_array[:, int(sub_array.shape[1] / 2):]
    east_num_white_pixels = east_sub_array.sum()

    # South
    south_sub_array = sub_array[int(sub_array.shape[0] / 2):, :]
    south_num_white_pixels = south_sub_array.sum()

    # West
    west_sub_array = sub_array[:, :int(sub_array.shape[1] / 2)]
    west_num_white_pixels = west_sub_array.sum()

    max_num_pixels = max(north_num_white_pixels, east_num_white_pixels,
                         south_num_white_pixels, west_num_white_pixels)

    if max_num_pixels == north_num_white_pixels:
        return image_analysis.Direction.NORTH

    if max_num_pixels == east_num_white_pixels:
        return image_analysis.Direction.EAST

    if max_num_pixels == south_num_white_pixels:
        return image_analysis.Direction.SOUTH

    if max_num_pixels == west_num_white_pixels:
        return image_analysis.Direction.WEST
