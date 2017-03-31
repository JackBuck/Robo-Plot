import operator
import math

import numpy as np
import cv2

import roboplot.config as config
import roboplot.core.hardware as hardware
import roboplot.core.camera.camera_utils as camera_utils
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.core.curves as curves


def compute_complete_path(image, centre, current_direction):
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
    # Convert the co-ordinates and append them move, make sure to use the centre as the photo may
    # have been take in the soft limits.
    computed_path = convert_to_global_coords(next_computed_pixel_path_segment,
                                             current_direction,
                                             centre,
                                             0,
                                             image_to_analyse.shape[1] / 2)
    fudge_distance = 0
    fudge_index = -1
    k = 0
    while fudge_distance < 20 and k < 200:  # Should be true but restricting path for debugging.
        k += 1
        if True: #try:
            # Move to new camera position and take photo.
            hardware.plotter.move_camera_to(computed_path[-1])
            image = hardware.plotter.take_photo_at(computed_path[-1])

            # Analyse photo to check if red is found.
            red_triangle_found, centre_of_red, bw_image = image_analysis.search_for_red_triangle_near_centre(image, red_min_size)

            if red_triangle_found:
                global_centre_of_red_list = convert_to_global_coords([centre_of_red],
                                                                     image_analysis.Direction.SOUTH,
                                                                     hardware.plotter._axes.current_location + config.CAMERA_OFFSET,
                                                                     int(image.shape[0] / 2),
                                                                     int(image.shape[1] / 2))

                global_centre_of_red = global_centre_of_red_list[0]
                computed_path.append(global_centre_of_red)
                break

             # Process image for analysis.
            image_to_analyse = image_analysis.process_image(bw_image)

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
                if len(next_computed_pixel_path_segment) > 1 and next_computed_pixel_path_segment[1][1] != -1:
                    camera_location = computed_path[-1]
                    candidate_path_segments[i] = convert_to_global_coords(next_computed_pixel_path_segment,
                                                                          current_direction,
                                                                          camera_location,
                                                                          0,
                                                                          sub_image.shape[1] / 2)

                    # Analyse candidate path.
                    length, is_valid_path = image_analysis.analyse_candidate_path(computed_path, candidate_path_segments[i])

                    if __debug__:
                        iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image.copy(), computed_path, False)

                        iadebug.save_candidate_line_approximation(hardware.plotter.debug_image.debug_image.copy(),
                                                                  computed_path, candidate_path_segments[i],  i)
                else:
                    is_valid_path = False

                if is_valid_path and length > selected_candidate_length:
                    selected_candidate = i
                    selected_candidate_length = length

            if selected_candidate == -1:

                if fudge_index is not -1 and fudge_index is not len(computed_path):
                    current_index = len(computed_path)
                    new_path_distance = 0
                    for i in range(fudge_index, current_index - 1):
                        new_path_distance += math.hypot(computed_path[i+1][0] - computed_path[i][0],
                                                        computed_path[i+1][1] - computed_path[i][1])

                    if new_path_distance < fudge_distance:
                        break
                    else:
                        fudge_distance = 0

                computed_path.pop()
                fudge_distance += math.hypot(computed_path[-1][0] - computed_path[-2][0],
                                             computed_path[-1][1] - computed_path[-2][1])

                fudge_index = len(computed_path)

            else:
                # Append the computed path with the new values.
                computed_path.extend(candidate_path_segments[selected_candidate])
                fudge_distance = 0


            if __debug__:
                iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image, computed_path, False)

        #except Exception as e:
        #    print('Exception: ' + str(e))
        #    break

    return computed_path


def follow_computed_path(computed_path):

    # Calculate and draw lines.
    line_segments = [curves.LineSegment(computed_path[i-1], computed_path[i])
                     for i in range(1, len(computed_path))]
    hardware.plotter.draw(line_segments)


def convert_to_global_coords(points, scan_direction, origin, y_offset, x_offset):

    # Scale factors
    x_scaling = config.X_PIXELS_TO_MILLIMETRE_SCALE
    y_scaling = config.Y_PIXELS_TO_MILLIMETRE_SCALE

    # Rotate and scale points to global orientation.
    if scan_direction is image_analysis.Direction.SOUTH:
        output_points = [list(map(operator.add, origin, ((y-y_offset) * y_scaling, (x - x_offset) * x_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis.Direction.EAST:
        output_points = [list(map(operator.add, origin, (-(x - x_offset) * x_scaling, (y-y_offset) * y_scaling)))
                         for y, x in points]
    elif scan_direction is image_analysis.Direction.WEST:
        output_points = [list(map(operator.add, origin, ((x - x_offset) * x_scaling, -(y-y_offset) * y_scaling)))
                         for y, x in points]
    else:
        output_points = [list(map(operator.add, origin, (-(y-y_offset) * y_scaling, -(x - x_offset) * x_scaling)))
                         for y, x in points]

    return output_points
