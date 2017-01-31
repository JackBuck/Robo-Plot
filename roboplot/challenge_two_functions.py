# coding=utf-8
import numpy as np
import roboplot.imgproc.image_processing as IP
import cv2
import math
import roboplot.imgproc.colour_detection as CD
import roboplot.core.Camera.camera_wrapper as camera_wrapper


a_camera = camera_wrapper.camera()

if __debug__:
    conversion_factor = 1.0
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


def find_green_triangle():
    """Walks around the perimeter of the paper and finds the green triangle
        Args:
            None
        Returns:
            np.ndarray: An 1x2 matrix representing the global co-ordinates of the centre of the green triangle.
        """

    # Calculate the list of positions photos need to be taken at to walk round the outside of the paper.
    camera_positions = IP.compute_positions(a4_height_y_mm, a4_width_x_mm, photo_size_mm)
    green_found = False

    # Walk round to each position and analyse the photo taken at that position.
    for i in range(0, len(camera_positions)):

        camera_centre = camera_positions[i]

        (displacement_x, displacement_y) = find_green_at_position(camera_centre)

        # Check if any green was detected.
        if displacement_x != -1:
            green_found = True
            break

    if not green_found:
        raise AssertionError("No green was found along perimeter")

    return camera_centre + displacement_x, camera_centre + displacement_y


def find_green_at_position(camera_centre):
    """Finds the centre of any green artifacts in the photo taken at the given position.
        Args:
            co - ordinates in global mm of camera location for photo.
        Returns:
            np.ndarray: An 1x2 matrix representing the global mm co-ordinates of the centre of the green artifact found.
            This is returned as (-1, -1) if no green found.
    """

    photo = a_camera.take_photo_at(camera_centre)

    # Create hsv version of image to analyse for colour detection.
    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)

    # Find the centre of the largest greed contour found on the image (if one exists)
    (cX, cY) = CD.detect_green(hsv_image, 5, True)

    # Check if any green was detected.
    if cX != -1:
        # Change to global mm co-ordinates from co-ordinates within photo.
        new_centre_x = (cX + camera_centre[0] - int(photo.shape[0] / 2)) * conversion_factor
        new_centre_y = (cY + camera_centre[1] - int(photo.shape[1] / 2)) * conversion_factor
        return new_centre_x, new_centre_y
    else:
        return -1, -1


def find_green_centre(initial_centre):

    error = 999999999

    camera_centre = initial_centre

    # While the new and old centres are not within 2 pixels of each other recheck the centre.
    while error < 2/conversion_factor:

        # Find the centre of the largest green contour found on the image (if one exists)
        new_centre = find_green_at_position(camera_centre)

        # Calculate the error between old centre and new centre
        error = math.sqrt((new_centre[0] - camera_centre[0])**2 + (new_centre[1] - camera_centre[1])**2)
        camera_centre = new_centre

    return camera_centre

