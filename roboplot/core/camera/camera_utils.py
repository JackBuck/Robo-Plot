# coding=utf-8
import os
import operator

import numpy as np
import cv2

import roboplot.config as config


def pad_image(image, target_photo_centre):
    """
    This function takes an image and the pixel indices of the target centre of the photo. It then pads and crops the
    image to achieve the required centre.
    Args:
        image: The image to be modified
        target_photo_centre: The target centre of the image

    Returns:
        modified_image: The image with the new centre.
    """

    # If the centre is already correct return early with the input image.
    if target_photo_centre[0] == int(image.shape[0] / 2) and target_photo_centre[1] == int(image.shape[1] / 2):
        return image

    # Otherwise create a modified image to populate with the required portion of the photo.
    modified_photo = np.zeros(image.shape, np.uint8)

    # Set min/max x value and placement in the photo
    if 0 > int(target_photo_centre[1]) - int(image.shape[1] / 2):
        # If the target location is lower in x than the current centre then the beginning of the image is used but
        # placed higher up the image in x.
        image_x_min = 0
        image_x_min_placement = int(image.shape[1] / 2 - int(target_photo_centre[1]))

        # The higher end of the image in x is cropped off and the remainder placed to the max edge in x of the
        # modified image
        image_x_max = int(target_photo_centre[1]) + int(image.shape[1] / 2)
        image_x_max_placement = image.shape[1]
    else:
        # If the target location is higher in x than the current centre then the beginning of the image cropped but
        # along the lower edge in x of the modified image.
        image_x_min = int(target_photo_centre[1]) - int(image.shape[1] / 2)
        image_x_min_placement = 0

        # The upper edge in x of the image used but placed lower in the image with the remainder filled with padding.
        image_x_max = image.shape[1]
        image_x_max_placement = image.shape[1] - (int(target_photo_centre[1]) - int(image.shape[1] / 2))

    # Set min/max y value and placement in the photo, reasoning as above but in y.
    if 0 > int(target_photo_centre[0]) - int(image.shape[0] / 2):
        image_y_min = 0
        image_y_max = int(target_photo_centre[0]) + int(image.shape[0] / 2)
        image_y_min_placement = int(image.shape[0] / 2 - int(target_photo_centre[0]))
        image_y_max_placement = image.shape[0]
    else:
        image_y_min = int(target_photo_centre[0]) - int(image.shape[0] / 2)
        image_y_max = image.shape[0]
        image_y_min_placement = 0
        image_y_max_placement = image.shape[0] - (int(target_photo_centre[0]) - int(image.shape[0] / 2))

    # Get dummy photo as sub array of the map.
    modified_photo[image_y_min_placement:image_y_max_placement, image_x_min_placement:image_x_max_placement] = \
        image[image_y_min:image_y_max, image_x_min:image_x_max]

    return modified_photo


def translate_camera_points_to_global_points(points):
    """
    This function takes a list of points and translates by the camera offset. This mean points recorded by the camera
    can now be followed/drawn by the plotter pen.
    Args:
        points: The list of points to be translated.

    Returns:
        global_points: The translated points.
    """

    global_points = [list(map(operator.add, point, config.camera_offset)) for point in points]

    return global_points
