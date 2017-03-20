# coding=utf-8
import os
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
    if target_photo_centre[0] == int(image.shape[0] / 2) and target_photo_centre[0] == int(image.shape[1] / 2):
        return image

    # Otherwise create a modified image to populate with the required portion of the photo.
    modified_photo = np.zeros(image.shape, np.uint8)

    # Set min/max x value and placement in the photo
    if 0 > int(target_photo_centre[1]) - int(image.shape[1] / 2):
        image_x_min = 0
        image_x_max = int(target_photo_centre[1]) + int(image.shape[1] / 2)
        # Simplification of int(self._photo_size - (camera_centre[0] + int(self._photo_size/2)))
        image_x_min_placement = int(image.shape[1] / 2 - int(target_photo_centre[1]))
        image_x_max_placement = image.shape[1]
    else:
        image_x_min = int(target_photo_centre[1]) - int(image.shape[1] / 2)
        image_x_max = image.shape[1]
        image_x_min_placement = 0
        image_x_max_placement = image.shape[1] - (int(target_photo_centre[1]) - int(image.shape[1] / 2))

    # Set min/max y value and placement in the photo
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
