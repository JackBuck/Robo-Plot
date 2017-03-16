import enum
import os
import math
import time
import operator

import numpy as np
import cv2

import roboplot.config as config
import roboplot.core.hardware as hardware
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.colour_detection as cd
import roboplot.core.curves as curves


def compute_complete_path(image, current_direction):
    # Set up variables.
    search_width = int(config.CAMERA_RESOLUTION[0]/2)
    red_triangle_found = False
    red_min_size = 30

    # Set up camera.
    a_camera = camera_wrapper.Camera()

    computed_path =[]

    i = 0
    while True:  # Should be true but restricting path for debugging.
        i += 1

        # Analyse photo to check if red is found.

        if len(image.shape) == 3:
            red_triangle_found, centre_of_red = image_analysis.search_for_red_triangle_near_centre(image, red_min_size)

        if red_triangle_found:
            global_centre_of_red = convert_to_global_coords(centre_of_red, current_direction,
                                                            hardware.both.axes.current_location)
            computed_path.append(centre_of_red)
            break

        # Process picture and extract image for analysis.
        image_to_analyse = image_analysis.process_and_extract_sub_image(image, current_direction)

        # Analyse image
        next_computed_pixel_path_segment, turn_to_next_direction = image_analysis.compute_pixel_path(image_to_analyse,
                                                                                                     search_width)
        next_computed_path_segment = convert_to_global_coords(next_computed_pixel_path_segment,
                                                              current_direction, hardware.both_axes.current_location)

        # Append the computed path with the new values.
        computed_path.extend(next_computed_path_segment)

        # Move to new camera position and take photo.
        line_segment = curves.LineSegment(hardware.both_axes.current_location, computed_path[-1])
        hardware.both_axes.follow(curve=line_segment, pen_speed=32)

        # Take next picture.
        image = a_camera.take_photo_at(hardware.both_axes.current_location)

        # Compute the current direction.
        if turn_to_next_direction == image_analysis.Turning.LEFT:
            current_direction = image_analysis.turn_left(current_direction)
        elif turn_to_next_direction == image_analysis.Turning.RIGHT:
            current_direction = image_analysis.turn_right(current_direction)

    if __debug__:
        iadebug.save_line_approximation(hardware.both_axes.debug_image.debug_image, computed_path)

    return computed_path


def follow_computed_path(computed_path):

    # Move to start of the computed path.
    line_segment = curves.LineSegment(hardware.both_axes.current_location,
                                      list(map(operator.sub, computed_path[0], config.camera_offset)))

    hardware.both_axes.follow(curve=line_segment, pen_speed=32)

    for i in range(1, len(computed_path)):
        # Move to next point in the computed path. # This can be updated when new follow exists.
        line_segment = curves.LineSegment(hardware.both_axes.current_location,
                                          list(map(operator.sub, computed_path[i], config.camera_offset)))
        hardware.both_axes.follow(curve=line_segment, pen_speed=32)


def convert_to_global_coords(points, scan_direction, origin):

    # Scale factors
    x_scaling = config.X_PIXELS_TO_MILLIMETRE_SCALE
    y_scaling = config.Y_PIXELS_TO_MILLIMETRE_SCALE

    offset = config.CAMERA_RESOLUTION[0]/2

    # Rotate and scale points to global orientation.
    if scan_direction is image_analysis.Direction.SOUTH:
        output_points = [list(map(operator.add, origin, (y * y_scaling, (x - offset) * x_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis.Direction.EAST:
        output_points = [list(map(operator.add, origin, (-(x - offset) * x_scaling, y * y_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis.Direction.WEST:
        output_points = [list(map(operator.add, origin, ((x - offset) * x_scaling, -y * y_scaling)))
                         for y, x in points]
    else:
        output_points = [list(map(operator.add, origin, (-y * y_scaling, -(x - offset) * x_scaling)))
                         for y, x in points]

    return output_points
