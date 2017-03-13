import enum
import os
import math
import time
import operator

import numpy as np
import cv2

import roboplot.config as config
import roboplot.core.hardware as hardware
import roboplot.core.camera_wrapper as camera_wrapper
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.colour_detection as cd
import roboplot.core.curves as curves


def compute_complete_path(image, starting_direction):
    # Set up variables.
    search_width = 100
    red_triangle_found = False
    red_min_size = 30

    # Set up camera.
    a_camera = camera_wrapper.Camera()

    # Analyse image where greed triangle was found and compute its path.
    image_to_analyse = image_analysis.process_and_extract_sub_image(image, starting_direction)
    computed_pixel_path, next_direction = image_analysis.compute_pixel_path(image, search_width)
    computed_path = transform_to_global_coords(computed_pixel_path, starting_direction,
                                                            hardware.both_axes.current_location)

    while True:

        current_direction = next_direction
        # Create the line segment and move to the last point in the found path.
        line_segment = curves.LineSegment(hardware.both_axes.current_location, computed_path[-1])
        hardware.both_axes.follow(curve=line_segment, pen_speed=32)

        # Take next picture.
        photo = a_camera.take_photo_at(hardware.both_axes.current_location)

        # Analyse photo to check if red is found.
        red_triangle_found, centre_of_red = image_analysis.search_for_red_triangle_on_path(photo, red_min_size)

        if red_triangle_found:
            computed_path.append(centre_of_red)
            break

        # Process picture and extract image for analysis.
        image_to_analyse = image_analysis.process_and_extract_sub_image(photo, next_direction)

        # Analyse image
        next_computed_pixel_path_segment, next_direction = image_analysis.compute_pixel_path(image, search_width)
        next_computed_path_segment = transform_to_global_coords(next_computed_path_segment, current_direction, hardware.both_axes.current_location

        # Append the computed path with the new values.
        computed_path.append(next_computed_path_segment)

    return computed_path


def follow_computed_path(computed_path):

    # Move to start of the computed path.
    line_segment = curves.LineSegment(hardware.both_axes.current_location, (computed_path[0][0] + config.)
    hardware.both_axes.follow(curve=line_segment, pen_speed=32)

    for i in range(1, len(computed_path)):
        # Move to next point in the computed path. # This can be updated when new follow exists.
        line_segment = curves.LineSegment(hardware.both_axes.current_location, (computed_path[0][0] + config.)
        hardware.both_axes.follow(curve=line_segment, pen_speed=32)


def transform_to_global_coords(computed_pixel_path, scan_direction, centre):
    # Rotate
    if scan_direction == image_analysis.Direction.NORTH:
        computed_points = [[centre[0] - point[0], centre[1] + point[1]]  for point in computed_pixel_path]
    elif scan_direction == image_analysis.Direction.EAST:
        computed_points = [[centre[1] + point[1], centre[0] + point[0]]  for point in computed_pixel_path]
    elif scan_direction == image_analysis.Direction.SOUTH:
        computed_points = [[centre[0] + point[0], centre[1] - point[1]]  for point in computed_pixel_path]
    else:
        computed_points = [[centre[1] - point[1], centre[0] - point[0]]  for point in computed_pixel_path]


    return computed_points