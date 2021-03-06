import enum
import os
import math
import time
import datetime

import numpy as np
import cv2

import roboplot.config as config
import roboplot.core.hardware as hardware

# Debugging scale factor
DEBUG_SCALE_FACTOR = 3


def save_line_approximation(debug_image, pixel_segments, is_rotated):
    """ Displays the line segments x = my + c on debug_image not this is assumed to already have been resized"""

    if debug_image is None:
        return

    # For each line segment draw a line between the start and end points of the segment and mark the start
    # and end with a circle. Ignore last pair as this is the target pair.

    for index in range(0, len(pixel_segments)-1):
        # Add artifacts to debug_image
        x_start_index = int(pixel_segments[index][1]*DEBUG_SCALE_FACTOR)
        y_start_index = int(pixel_segments[index][0]*DEBUG_SCALE_FACTOR)
        x_end_index = int(pixel_segments[index + 1][1]*DEBUG_SCALE_FACTOR)
        y_end_index = int(pixel_segments[index + 1][0]*DEBUG_SCALE_FACTOR)

        # Note these functions need the co-ordinates ordered (x, y)
        cv2.line(debug_image, (x_start_index, y_start_index), (x_end_index, y_end_index), (255, 10, 10), 1)
        cv2.circle(debug_image, (x_start_index, y_start_index), 2, (255, 10, 10))
        cv2.circle(debug_image, (x_end_index, y_end_index), 2, (255, 10, 10))


    filename = datetime.datetime.now().strftime("%M%S.%f_") \
               + str(hardware.plotter._axes.current_location[0]) \
               + '_' \
               + str(hardware.plotter._axes.current_location[1]) + '_'

    if is_rotated:
        filename += 'line_approximation_rotated' + '.jpg'
    else:
        filename += 'line_approximation' + '.jpg'

    cv2.imwrite(os.path.join(config.debug_output_folder, filename), debug_image)


def save_candidate_line_approximation(debug_image, pixel_segments, candidate_segments, i):
    """ Displays the line segments x = my + c on debug_image not this is assumed to already have been resized"""

    if debug_image is None:
        return

    # For each line segment draw a line between the start and end points of the segment and mark the start
    # and end with a circle. Ignore last pair as this is the target pair.

    for index in range(0, len(pixel_segments) - 1):
        # Add artifacts to debug_image
        x_start_index = int(pixel_segments[index][1]*DEBUG_SCALE_FACTOR)
        y_start_index = int(pixel_segments[index][0]*DEBUG_SCALE_FACTOR)
        x_end_index = int(pixel_segments[index + 1][1]*DEBUG_SCALE_FACTOR)
        y_end_index = int(pixel_segments[index + 1][0]*DEBUG_SCALE_FACTOR)

        # Note these functions need the co-ordinates ordered (x, y)
        cv2.line(debug_image, (x_start_index, y_start_index), (x_end_index, y_end_index), (255, 10, 10), 1)
        cv2.circle(debug_image, (x_start_index, y_start_index), 2, (255, 10, 10))

    for index in range(0, len(candidate_segments) - 1):
        # Add artifacts to debug_image
        x_start_index = int(candidate_segments[index][1]*DEBUG_SCALE_FACTOR)
        y_start_index = int(candidate_segments[index][0]*DEBUG_SCALE_FACTOR)
        x_end_index = int(candidate_segments[index + 1][1]*DEBUG_SCALE_FACTOR)
        y_end_index = int(candidate_segments[index + 1][0]*DEBUG_SCALE_FACTOR)

        # Note these functions need the co-ordinates ordered (x, y)
        cv2.line(debug_image, (x_start_index, y_start_index), (x_end_index, y_end_index), (10, 240, 10), 1)
        cv2.circle(debug_image, (x_start_index, y_start_index), 2, (10, 240, 10))




    filename = datetime.datetime.now().strftime("%M%S.%f_") \
               + str(hardware.plotter._axes.current_location[0]) \
               + '_' \
               + str(hardware.plotter._axes.current_location[1]) + '_Direction' + str(i) + '.jpg'



    cv2.imwrite(os.path.join(config.debug_output_folder, filename), debug_image)


def save_average_rows(image, indices, is_rotated):
    # resize so the result can be seen

    debug_image = create_debug_image(image)
    for i in range(0, len(indices) - 1):
        current_average_pixel = indices[i][1] * DEBUG_SCALE_FACTOR
        for pixel in range(-1, 1):
            if (current_average_pixel + pixel > 0) and (current_average_pixel + pixel < debug_image.shape[1]):
                for j in range(0, DEBUG_SCALE_FACTOR):
                    debug_image[int(DEBUG_SCALE_FACTOR * indices[i][0] + j),
                                int(current_average_pixel + pixel)] = (10, 10, 255)

    filename = datetime.datetime.now().strftime("%M%S.%f_") \
               + str(hardware.plotter._axes.current_location[0]) \
               + '_' \
               + str(hardware.plotter._axes.current_location[1]) + '_'

    if is_rotated:
        filename += 'average_rows_rotated' + '.jpg'
    else:
        filename += 'average_rows' + '.jpg'
    cv2.imwrite(os.path.join(config.debug_output_folder, filename),
                debug_image)

    #cv2.imshow('Average Rows', debug_image)
    #cv2.waitKey(0)

    return debug_image

def save_sub_image(image):

    filename = datetime.datetime.now().strftime("%M%S.%f_") \
               + str(hardware.plotter._axes.current_location[0]) \
               + '_' \
               + str(hardware.plotter._axes.current_location[1]) + '_SubImage.jpg'

    cv2.imwrite(os.path.join(config.debug_output_folder,filename), image)


def save_processed_image(image):

    filename = datetime.datetime.now().strftime("%M%S.%f_") \
               + str(hardware.plotter._axes.current_location[0]) \
               + '_' \
               + str(hardware.plotter._axes.current_location[1]) + '_Processed_Image.jpg'

    cv2.imwrite(os.path.join(config.debug_output_folder, filename), image)

def create_debug_image(image):
    debug_image = cv2.resize(image, (0, 0), fx=DEBUG_SCALE_FACTOR, fy=DEBUG_SCALE_FACTOR)
    debug_image = cv2.cvtColor(debug_image, cv2.COLOR_GRAY2BGR)
    return debug_image
