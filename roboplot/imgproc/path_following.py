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
    computed_path =[]
    direction_turned = image_analysis.Turning.STRAIGHT

    i = 0
    while i<30:  # Should be true but restricting path for debugging.
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

        if next_computed_pixel_path_segment[0][0] == -1:
            # Try another orientation of the current image - not currently you could end up infinitely looping round
            # with the wrong parameters. Dont come back the way you came.

            # Compute the current direction.
            if direction_turned == image_analysis.Turning.LEFT:
                current_direction = image_analysis.turn_right(current_direction)
            elif direction_turned == image_analysis.Turning.RIGHT:
                current_direction = image_analysis.turn_left(current_direction)

        else:
            #Continue as usual - convert the co-ordinates and append them move

            camera_location = hardware.plotter._axes.current_location + config.CAMERA_OFFSET
            next_computed_path_segment = convert_to_global_coords(next_computed_pixel_path_segment,
                                                                  current_direction,
                                                                  camera_location)

            # Append the computed path with the new values.
            computed_path.extend(next_computed_path_segment)

            # Move to new camera position and take photo.
            hardware.plotter.move_camera_to(computed_path[-1])

            # Compute the current direction.
            if turn_to_next_direction == image_analysis.Turning.LEFT:
                current_direction = image_analysis.turn_left(current_direction)
            elif turn_to_next_direction == image_analysis.Turning.RIGHT:
                current_direction = image_analysis.turn_right(current_direction)

            direction_turned = turn_to_next_direction

        # Take next picture. - We have to do this even if we havent moved as otherwise we will process it twice.
        image = hardware.plotter.take_photo_at(computed_path[-1])

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
