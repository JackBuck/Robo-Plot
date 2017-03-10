import enum
import os
import math
import time

import numpy as np
import cv2

import roboplot.config as config


def show_line_approximation(image, pixel_segments):
    """ Displays the line segments x = my + c on debug_image"""

    if image is None:
        return

    # Create copy of debug_image with averages marked on.
    debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # resize so the result can be seen

    resize_factor = 3
    resized_image = cv2.resize(debug_image, (0, 0), fx=resize_factor, fy=resize_factor)

    # For each line segment draw a line between the start and end points of the segment and mark the start
    # and end with a circle. Ignore last pair as this is the target pair.

    for index in range(0, len(pixel_segments) - 2):
        # Add artifacts to debug_image
        x_start_index = int(pixel_segments[index][1]*resize_factor)
        y_start_index = int(pixel_segments[index][0]*resize_factor)
        x_end_index = int(pixel_segments[index + 1][1]*resize_factor)
        y_end_index = int(pixel_segments[index + 1][0]*resize_factor)

        # Note these functions need the co-ordinates ordered (x, y)
        cv2.line(resized_image, (x_start_index, y_start_index), (x_end_index, y_end_index), (255, 10, 10), 2)
        cv2.circle(resized_image, (x_start_index, y_start_index), 3, (255, 10, 10))

    cv2.circle(resized_image, (int(pixel_segments[-1][0]*resize_factor),
                               int(pixel_segments[-1][1]*resize_factor)), 4, (255, 10, 10))

    cv2.imshow('LineApproximation', resized_image)
    cv2.waitKey(0)
    cv2.imwrite(os.path.join(config.debug_output_folder, 'sub_image' + time.strftime("%Y%m%d-%H%M%S") + '.jpg'),
                resized_image)


def show_average_rows(image, indices):
    # resize so the result can be seen
    resize_factor = 3
    debug_image = cv2.resize(image, (0, 0), fx=resize_factor, fy=resize_factor)
    debug_image = cv2.cvtColor(debug_image, cv2.COLOR_GRAY2BGR)
    for i in range(0, len(indices) - 1):
        current_average_pixel = indices[i][1] * resize_factor
        for pixel in range(-1, 1):
            if (current_average_pixel + pixel > 0) and (current_average_pixel + pixel < debug_image.shape[1]):
                for j in range(0, resize_factor):
                    debug_image[int(resize_factor * indices[i][0] + j), int(current_average_pixel + pixel)] = (10, 10, 255)
    cv2.imwrite(os.path.join(config.debug_output_folder, 'AverageRows' + time.strftime("%Y%m%d-%H%M%S") + '.jpg'),
                debug_image)
    cv2.imshow('Average Rows', debug_image)
    cv2.waitKey(0)

    return debug_image
