import math

import cv2
import numpy as np

import roboplot.config as config
import roboplot.core.camera.camera_utils
import roboplot.imgproc.image_analysis_enums as image_analysis_enums
import roboplot.imgproc.page_search as page_search
import roboplot.core.hardware as hardware
import roboplot.imgproc.colour_detection as colour_detection


# Define the paper and photo size. - This will be moved out of here eventually.
# Paper orientation and axis.
#  __________
# |          |
# |          |
# |          |
# |          |
# ^          |
# |          |
# O--->  ----|

a4_height_y_mm = 297
a4_width_x_mm = 210
photo_size_mm = 40


def find_green_triangle(min_size):
    """

    Args:
        min_size: minimum size of artifact to recognise

    Returns:
        global co-ordinates of centre of the green artifact recognise

    """

    # Calculate the list of positions photos need to be taken at to walk round the outside of the paper.
    camera_positions = page_search.compute_positions(a4_width_x_mm, a4_height_y_mm, photo_size_mm)

    green_found = False
    green_position = [-1, -1]

    # Walk round to each position and analyse the photo taken at that position.
    for i in range(0, len(camera_positions)):

        camera_centre = camera_positions[i]

        green_position, photo = find_green_at_position(camera_centre, min_size)

        # Check if any green was detected.
        if green_position[0] != -1:
            green_found = True
            break

    if not green_found:
        raise AssertionError("No green was found on paper")

    return green_position


def find_red_at_position(camera_centre, min_size):
    """Finds the centre of any green artifacts in the photo taken at the given position.
        Args:
            co - ordinates in global mm of camera location for photo.
        Returns:
            np.ndarray: An 1x2 matrix representing global co-ordinates of the centre of the green.
            This is returned as (-1, -1) if no green found.
    """

    # Move to camera position
    if not np.array_equal(hardware.plotter._axes.current_location + config.CAMERA_OFFSET, camera_centre):
        hardware.plotter.move_camera_to(camera_centre)

    photo = hardware.plotter.take_photo_at(camera_centre)

    # Create hsv version of image to analyse for colour detection.
    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)

    # Find the centre of the largest green contour found on the image (if one exists)
    (cX, cY) = colour_detection.detect_red(hsv_image, min_size, True)

    if cX != -1:
        new_centre_list = roboplot.core.camera.camera_utils.convert_to_global_coords([[cY, cX]],
                                                                                     image_analysis_enums.Direction.SOUTH,
                                                                                     camera_centre,
                                                                                     int(photo.shape[0] / 2),
                                                                                     int(photo.shape[1] / 2))
        new_centre = new_centre_list[0]
    else:
        new_centre = [cX, cY]

    return new_centre, hsv_image[:, :, 2]


def find_green_at_position(camera_centre, min_size):
    """Finds the centre of any green artifacts in the photo taken at the given position.
        Args:
            co - ordinates in global mm of camera location for photo.
        Returns:
            np.ndarray: An 1x2 matrix representing global co-ordinates of the centre of the green.
            This is returned as (-1, -1) if no green found.
    """

    # Move to camera position
    if not np.array_equal(hardware.plotter._axes.current_location + config.CAMERA_OFFSET, camera_centre):
        hardware.plotter.move_camera_to(camera_centre)

    photo = hardware.plotter.take_photo_at(camera_centre)

    # Create hsv version of image to analyse for colour detection.
    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)

    # Find the centre of the largest green contour found on the image (if one exists)
    (cX, cY) = colour_detection.detect_green(hsv_image, min_size, True)

    if cX != -1:
        new_centre_list = roboplot.core.camera.camera_utils.convert_to_global_coords([[cY, cX]],
                                                                                     image_analysis_enums.Direction.SOUTH,
                                                                                     camera_centre,
                                                                                     int(photo.shape[0] / 2),
                                                                                     int(photo.shape[1] / 2))
        new_centre = new_centre_list[0]
    else:
        new_centre = [cX, cY]

    return new_centre, hsv_image[:, :, 2]


def find_green_centre(initial_centre, min_size):

    error = 999999999

    camera_centre = initial_centre
    photo = None

    # While the new and old centres are not within 2 pixels of each other recheck the centre.
    i = 0
    while i < 3 and error > 2:

        # Find the centre of the largest green contour found on the image (if one exists)
        new_centre, photo = find_green_at_position(camera_centre, min_size)

        # Calculate the error between old centre and new centre
        error = math.sqrt((new_centre[0] - camera_centre[0])**2 + (new_centre[1] - camera_centre[1])**2)
        camera_centre = new_centre

        i += 1

    return camera_centre, photo


def find_red_centre(initial_centre, min_size):

    error = 999999999

    camera_centre = initial_centre
    photo = None

    # While the new and old centres are not within 2 pixels of each other recheck the centre.
    i = 0
    while i < 3 and error > 2:

        # Find the centre of the largest green contour found on the image (if one exists)
        new_centre, photo = find_red_at_position(camera_centre, min_size)

        # Calculate the error between old centre and new centre
        error = math.sqrt((new_centre[0] - camera_centre[0])**2 + (new_centre[1] - camera_centre[1])**2)
        camera_centre = new_centre

        i += 1

    return camera_centre, photo



