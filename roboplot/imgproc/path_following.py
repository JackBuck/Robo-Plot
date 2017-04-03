import math
import operator

import cv2
import numpy as np

import roboplot.config as config
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.image_analysis_enums as image_analysis_enums
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.start_end_detection as start_end_detection
from roboplot.core.camera.camera_utils import convert_to_global_coords


class PathFinder:
    reanalysis_index = -1
    back_tracked_distance = 0
    reanalysis_distance = 0
    reanalysis_attempts = 0

    def follow_computed_path(self, computed_path):
        """
        This function takes the computed path and draw it with the pen.
        Args:
            computed_path: The path to follow.
        Returns:
        """
        # Calculate and draw lines.
        line_segments = [curves.LineSegment(computed_path[i - 1], computed_path[i])
                         for i in range(1, len(computed_path))]
        hardware.plotter.draw(line_segments)

    def calculate_path_from_image(self, image_to_analyse, search_width, computed_path, rotation_deg=0):
        """

        Args:
            image_to_analyse: The image to find the next bit of path from.
            search_width: The width used to find the path when not found at the centre of the image.
            computed_path: The path computed so far.

        Returns:
            A new section of path, if a valid path was found.
        """

        # Rotate image if required.
        if rotation_deg is not 0:
            # Rotation transform requires x then y.
            M = cv2.getRotationMatrix2D((image_to_analyse.shape[1]/2, image_to_analyse.shape[0]/2), rotation_deg, 1.0)

            w = image_to_analyse.shape[1]
            h = image_to_analyse.shape[0]
            image_to_analyse = cv2.warpAffine(image_to_analyse, M, (w, h))

            iadebug.save_processed_image(image_to_analyse)

        # Analyse image in all four directions.
        candidate_path_segments = [[], [], [], []]
        selected_candidate = -1
        selected_candidate_length = -1

        for i in range(0, 4):
            # Extract sub image.
            current_direction = image_analysis_enums.Direction(i)
            sub_image = image_analysis.extract_sub_image(image_to_analyse, current_direction)
            next_computed_pixel_path_segment, turn_to_next_direction = image_analysis.compute_pixel_path(
                sub_image,
                search_width)

            # Rotate line indices back.
            if rotation_deg is not 0:
                centre = (image_to_analyse.shape[0] / 2, image_to_analyse.shape[1] / 2)
                next_computed_pixel_path_segment = [image_analysis.rotate(centre, point, -np.deg2rad(rotation_deg))
                                                    for point in next_computed_pixel_path_segment]

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
                    iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image.copy(), computed_path,
                                                    False)
                    iadebug.save_candidate_line_approximation(hardware.plotter.debug_image.debug_image.copy(),
                                                              computed_path, candidate_path_segments[i], i)
            else:
                is_valid_path = False

            if is_valid_path and length > selected_candidate_length:
                selected_candidate = i
                selected_candidate_length = length

        if selected_candidate == -1:
            return False, None
        else:
            return True, candidate_path_segments[selected_candidate]

    def find_offset_positions(self, computed_path):

        total_num_position = 1
        offset_positions = []
        current_segment = -1
        offset_distance = 1

        current_retrace_length = 0

        while offset_distance < total_num_position + 1:
            length = math.hypot(computed_path[current_segment][0] - computed_path[current_segment - 1][0],
                                computed_path[current_segment][1] - computed_path[current_segment - 1][1])

            while offset_distance < current_retrace_length + length and offset_distance < total_num_position + 1:
                proportion = (offset_distance - current_retrace_length)/length
                new_position = list(computed_path[current_segment]
                                    + (np.array(computed_path[current_segment - 1])
                                       - computed_path[current_segment])*proportion)

                offset_positions.append(new_position)
                offset_distance += 1

            current_retrace_length += length

        return offset_positions

    def compute_complete_path(self, image, centre):
        """

        Args:
            image: The image containing the path start.
            centre: The centre of the image in mm. Note this could be different to the current location due to
            soft limits and padding.

        Returns:
            computed_path: A list of co-ordinates representing the calculated path.
        """

        # Set up variables.
        search_width = 15/config.X_PIXELS_TO_MILLIMETRE_SCALE
        red_min_size = 30

        computed_path = [centre]
        # Process picture and extract image for analysis.
        image_to_analyse = image

        path_found, new_path = self.calculate_path_from_image(image_to_analyse, search_width, computed_path)
        if path_found:
            # Only add the first 5 mm of path as the uneroded path gives errors.

            path_length = 0
            for i in range(len(new_path) - 1):
                segment_length = math.hypot(new_path[i][0] - new_path[i+1][0], new_path[i+1][1] - new_path[i+1][1])

                if (path_length + segment_length) > 2:
                    distance_along_segment = 2 - path_length
                    proportion = distance_along_segment/segment_length

                    new_point = list(np.array(new_path[i])*proportion + np.array(new_path[i+1])*(1-proportion))
                    new_path = new_path[:i]
                    new_path.append(new_point)
                    break

                path_length += segment_length

            computed_path.extend(new_path)
        else:
            return

        self.reanalysis_index = -1
        self.back_tracked_distance = 0
        self.reanalysis_distance = 0
        self.reanalysis_attempts = 0

        k = 0
        while self.reanalysis_attempts < 5 and k < 200:  # Should be true but restricting path/ stop eternal loops.
            k += 1
            if True: #try:
                # Move to new camera position and take photo.
                hardware.plotter.move_camera_to(computed_path[-1])
                image = hardware.plotter.take_photo_at(computed_path[-1])

                # Analyse photo to check if red is found.
                red_triangle_found, centre_of_red, bw_image = image_analysis.search_for_red_triangle_near_centre(image, red_min_size)

                if red_triangle_found:
                    global_centre_of_red_list = convert_to_global_coords([centre_of_red],
                                                                         image_analysis_enums.Direction.SOUTH,
                                                                         hardware.plotter._axes.current_location + config.CAMERA_OFFSET,
                                                                         int(image.shape[0] / 2),
                                                                         int(image.shape[1] / 2))

                    global_centre_of_red, _ = start_end_detection.find_red_centre(global_centre_of_red_list[0], min_size=10)
                    computed_path.append(global_centre_of_red)
                    break

                # Process image for analysis.
                image_to_analyse = image_analysis.process_image(bw_image)

                path_found, new_path = self.calculate_path_from_image(image_to_analyse, search_width, computed_path)

                if not path_found:
                    break
                    #for i in range(0, 4):
#
                    #    # Search for new path. - THIS CANNOT BE DONE WITH UNERODED IMAGE.
                    #    path_found, new_path = self.calculate_path_from_image(image_to_analyse, search_width,
                    #                                                          computed_path, rotation_deg=i*20)
#
                    #    if path_found:
                    #        break
#
                    #if not path_found:
#
                    #    # Break loop and draw what we have found.
                    #    break

                computed_path.extend(new_path)

                if __debug__:
                    iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image.copy(), computed_path,
                                                    False)

            #except Exception as e:
            #    print('Exception: ' + str(e))
            #    break

        return computed_path



