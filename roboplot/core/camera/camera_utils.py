# coding=utf-8
import operator

import numpy as np

from roboplot import config as config
from roboplot.imgproc import image_analysis_enums as image_analysis_enums

default_padding_grey_value = 30


def pad_image(image: np.ndarray,
              target_photo_centre: (float, float),
              grey_value: np.uint8 = default_padding_grey_value) -> np.ndarray:
    """
    This function takes an image and the pixel indices of the target centre of the photo. It then pads and crops the
    image to achieve the required centre.

    Args:
        image: the image to be modified
        target_photo_centre: the target centre (row,col) of the image in pixels
        grey_value: the gray value used to pad the image

    Returns:
        np.ndarray: the modified image with the new centre.
    """

    # If the centre is already correct return early with the input image.
    if target_photo_centre[0] == int(image.shape[0] / 2) and target_photo_centre[1] == int(image.shape[1] / 2):
        return image

    # Otherwise create a modified image to populate with the required portion of the photo.
    modified_photo = np.zeros(image.shape, np.uint8)
    modified_photo.fill(grey_value)

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

    global_points = [list(map(operator.add, point, config.CAMERA_OFFSET)) for point in points]

    return global_points


def convert_to_global_coords(points, scan_direction, origin, y_offset, x_offset):

    # Scale factors
    x_scaling = config.X_PIXELS_TO_MILLIMETRE_SCALE
    y_scaling = config.Y_PIXELS_TO_MILLIMETRE_SCALE

    # Rotate and scale points to global orientation.
    if scan_direction is image_analysis_enums.Direction.SOUTH:
        output_points = [list(map(operator.add, origin, ((y-y_offset) * y_scaling, (x - x_offset) * x_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis_enums.Direction.EAST:
        output_points = [list(map(operator.add, origin, (-(x - x_offset) * x_scaling, (y-y_offset) * y_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis_enums.Direction.WEST:
        output_points = [list(map(operator.add, origin, ((x - x_offset) * x_scaling, -(y-y_offset) * y_scaling)))
                         for y, x in points]
    else:
        output_points = [list(map(operator.add, origin, (-(y-y_offset) * y_scaling, -(x - x_offset) * x_scaling)))
                         for y, x in points]

    return output_points
