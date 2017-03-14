# coding=utf-8
import math

import numpy as np
import cv2

import roboplot.imgproc.image_analysis as IP
import roboplot.imgproc.colour_detection as CD
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.page_search as page_search
import roboplot.core.curves as curves
import roboplot.core.gpio.gpio_wrapper as gpio_wrapper
import roboplot.core.hardware as hardware

a_camera = camera_wrapper.Camera()

if __debug__:
    conversion_factor = 0.05
else:
    # Converts from pixels in image to mm. (Based on an image 4cm x 4cm and 200 x 200 pixels)
    # This will need to be calibrated.
    conversion_factor = 0.2


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


def find_green_triangle(pen_speed, min_size):
    """

    Args:
        pen_speed: speed to move
        min_size: minimum size of artifact to recognise

    Returns:
        global co-ordinates of centre of the green artifact recognise

    """

    # Calculate the list of positions photos need to be taken at to walk round the outside of the paper.
    camera_positions = page_search.compute_positions(a4_width_x_mm, a4_height_y_mm, photo_size_mm)
    green_found = False

    # Walk round to each position and analyse the photo taken at that position.
    for i in range(0, len(camera_positions)):

        camera_centre = camera_positions[i]

        displacement_x, displacement_y, photo = find_green_at_position(camera_centre, pen_speed, min_size)

        # Check if any green was detected.
        if displacement_x != -1:
            green_found = True
            break

    if not green_found:
        raise AssertionError("No green was found on paper")

    return camera_centre[0] + displacement_y, camera_centre[1] + displacement_x


def find_green_at_position(camera_centre, pen_speed, min_size):
    """Finds the centre of any green artifacts in the photo taken at the given position.
        Args:
            co - ordinates in global mm of camera location for photo.
        Returns:
            np.ndarray: An 1x2 matrix representing the global mm co-ordinates of the centre of the green artifact found.
            This is returned as (-1, -1) if no green found.
    """

    # Move to camera position

    if not np.array_equal(hardware.both_axes.current_location, camera_centre):
        print(camera_centre)
        line_to_camera_position = curves.LineSegment(hardware.both_axes.current_location, camera_centre)
        hardware.both_axes.follow(curve=line_to_camera_position, pen_speed=pen_speed)

    photo = a_camera.take_photo_at(hardware.both_axes.current_location)

    # Create hsv version of image to analyse for colour detection.
    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)

    # Find the centre of the largest greed contour found on the image (if one exists)
    (cX, cY) = CD.detect_green(hsv_image, min_size/conversion_factor, True)

    # Check if any green was detected.
    if cX != -1:
        # Change to global mm co-ordinates from co-ordinates within photo.
        displacement_x = (cX - int(photo.shape[0] / 2))*conversion_factor
        displacement_y = (cY - int(photo.shape[1] / 2))*conversion_factor

        return displacement_x, displacement_y, photo
    else:
        return -1, -1, photo


def find_green_centre(initial_centre, pen_speed, min_size):

    error = 999999999

    camera_centre = initial_centre

    # While the new and old centres are not within 2 pixels of each other recheck the centre.
    while error > 2/conversion_factor:

        # Find the centre of the largest green contour found on the image (if one exists)
        displacement_x, displacement_y, photo = find_green_at_position(camera_centre, pen_speed, min_size)
        new_centre = (camera_centre[0] + displacement_y, camera_centre[1] + displacement_x)

        # Calculate the error between old centre and new centre
        error = math.sqrt((new_centre[0] - camera_centre[0])**2 + (new_centre[1] - camera_centre[1])**2)
        camera_centre = new_centre

    return camera_centre, photo

