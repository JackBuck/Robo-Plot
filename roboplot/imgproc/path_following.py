import operator

import numpy as np
import cv2

import roboplot.config as config
import roboplot.core.hardware as hardware
import roboplot.core.camera.camera_utils as camera_utils
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.core.curves as curves


def compute_complete_path(image, current_direction):
    # Set up variables.
    search_width = int(config.CAMERA_RESOLUTION[0]/5)
    red_triangle_found = False
    red_min_size = 30

    kernel = np.ones((5, 5), np.uint8)
    image = cv2.dilate(image, kernel, iterations=10)

    # Process picture and extract image for analysis.
    image_to_analyse = image_analysis.process_image(image)
    image_to_analyse = image_analysis.extract_sub_image(image_to_analyse, current_direction)

    # Analyse image
    next_computed_pixel_path_segment, turn_to_next_direction = image_analysis.compute_pixel_path(image_to_analyse,
                                                                                                 search_width)
    # Convert the co-ordinates and append them move
    camera_location = hardware.plotter._axes.current_location + config.CAMERA_OFFSET
    computed_path = convert_to_global_coords(next_computed_pixel_path_segment,
                                                          current_direction,
                                                          camera_location)
    k = 0
    while k<30:  # Should be true but restricting path for debugging.
        k += 1

        # Move to new camera position and take photo.
        hardware.plotter.move_camera_to(computed_path[-1])
        image = hardware.plotter.take_photo_at(computed_path[-1])

        # Analyse photo to check if red is found.

        if len(image.shape) == 3:
            red_triangle_found, centre_of_red = image_analysis.search_for_red_triangle_near_centre(image, red_min_size)

        if red_triangle_found:
            global_centre_of_red = convert_to_global_coords(centre_of_red, current_direction,
                                                            hardware.both_axes.current_location)
            computed_path.append(centre_of_red)
            break


         # Process image for analysis.
        image_to_analyse = image_analysis.process_image(image)

        # Analyse image in all four directions.

        candidate_path_segments = [[], [], [], []]
        selected_candidate = -1
        selected_candidate_length = -1
        for i in range(0, 4):
            # Extract sub image.
            current_direction = image_analysis.Direction(i)
            sub_image = image_analysis.extract_sub_image(image_to_analyse, current_direction)

            next_computed_pixel_path_segment, turn_to_next_direction = image_analysis.compute_pixel_path(
                sub_image,
                search_width)

            # Convert the co-ordinates.
            camera_location = hardware.plotter._axes.current_location + config.CAMERA_OFFSET
            candidate_path_segments[i] = convert_to_global_coords(next_computed_pixel_path_segment,
                                                                  current_direction,
                                                                  camera_location)

            # Analyse candidate path.
            length, is_valid_path = image_analysis.analyse_candidate_path(computed_path, candidate_path_segments[i])

            if __debug__:
                iadebug.save_line_approximation(hardware.plotter._axes.debug_image.debug_image.copy(), computed_path, False)

                temp_path = computed_path.copy()
                temp_path.extend(candidate_path_segments[i])
                iadebug.save_candidate_line_approximation(hardware.plotter._axes.debug_image.debug_image.copy(),
                                                          temp_path, i)

            if is_valid_path and length > selected_candidate_length:
                selected_candidate = i
                selected_candidate_length = length


        # Append the computed path with the new values.
        computed_path.extend(candidate_path_segments[selected_candidate])

        if __debug__:
            iadebug.save_line_approximation(hardware.plotter._axes.debug_image.debug_image, computed_path, False)

    return computed_path


def follow_computed_path(computed_path):

    # Move to start of the computed path.
    hardware.plotter.move_pen_to(computed_path[0])

    # Move to next point in the computed path. # This can be updated when new follow exists.
    line_segments = [curves.LineSegment(hardware.plotter._axes.current_location,
                                       list(map(operator.sub, point, config.CAMERA_OFFSET)))
                    for point in computed_path]

    hardware.plotter.draw(line_segments)


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
