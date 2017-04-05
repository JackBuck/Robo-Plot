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
    computed_path = []
    search_width = 15 / config.X_PIXELS_TO_MILLIMETRE_SCALE
    removal_count = 0
    path_end_position_at_last_removal = [10000000000, 1000000000]

    def follow_computed_path(self):
        """
        This function follows the internal computed path with the pen.
        Args:
        Returns:
        """
        # Calculate and draw lines.
        line_segments = [curves.LineSegment(self.computed_path[i - 1], self.computed_path[i])
                         for i in range(1, len(self.computed_path))]
        hardware.plotter.draw(line_segments)

    def calculate_path_from_image(self, image_to_analyse, rotation_deg=0):
        """

        Args:
            image_to_analyse: The image to find the next bit of path from.
            rotation_deg: The rotation to apply to the image before processing.

        Returns:
            A new section of path, if a valid path was found.
        """

        # Rotate image if required.
        if rotation_deg is not 0:
            # Rotation transform requires x then y.
            M = cv2.getRotationMatrix2D((image_to_analyse.shape[1] / 2, image_to_analyse.shape[0] / 2), rotation_deg,
                                        1.0)

            w = image_to_analyse.shape[1]
            h = image_to_analyse.shape[0]
            image_to_analyse = cv2.warpAffine(image_to_analyse, M, (w, h))

            iadebug.save_processed_image(image_to_analyse)

        # Analyse image in all four directions.
        candidate_path_segments = [[], [], [], []]
        selected_candidate = -1
        selected_candidate_length = -1
        num_point_in_selected_candidate = 1000000

        for i in range(0, 4):
            # Extract sub image.
            current_direction = image_analysis_enums.Direction(i)
            sub_image = image_analysis.extract_sub_image(image_to_analyse, current_direction)
            rotated_computed_pixel_path_segment, turn_to_next_direction = image_analysis.compute_pixel_path(
                sub_image,
                self.search_width)

            # Rotate line indices back.
            if rotation_deg is not 0 and rotated_computed_pixel_path_segment[1][1] != -1:
                centre = (0, image_to_analyse.shape[1] / 2)
                next_computed_pixel_path_segment = [image_analysis.rotate(centre, point, np.deg2rad(-rotation_deg))
                                                    for point in rotated_computed_pixel_path_segment]
            else:
                next_computed_pixel_path_segment = rotated_computed_pixel_path_segment

            # Convert the co-ordinates.
            if len(next_computed_pixel_path_segment) > 1 and rotated_computed_pixel_path_segment[1][1] != -1:
                camera_location = self.computed_path[-1]
                candidate_path_segments[i] = convert_to_global_coords(next_computed_pixel_path_segment,
                                                                      current_direction,
                                                                      camera_location,
                                                                      0,
                                                                      sub_image.shape[1] / 2)

                # Analyse candidate path.
                length, is_valid_path = image_analysis.analyse_candidate_path(self.computed_path,
                                                                              candidate_path_segments[i])
                if __debug__:
                    iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image.copy(), self.computed_path,
                                                    False)
                    iadebug.save_candidate_line_approximation(hardware.plotter.debug_image.debug_image.copy(),
                                                              self.computed_path, candidate_path_segments[i], i)
            else:
                is_valid_path = False

            update_selected_path = False
            if is_valid_path:
                if length - selected_candidate_length > 3:
                    update_selected_path = True
                elif -3 < length - selected_candidate_length <= 3:
                    if len(candidate_path_segments[i]) < num_point_in_selected_candidate:
                        update_selected_path = True

            if update_selected_path:
                selected_candidate = i
                num_point_in_selected_candidate = len(candidate_path_segments[i])
                selected_candidate_length = length

        if selected_candidate == -1:
            return False, None
        else:
            return True, candidate_path_segments[selected_candidate]

    def find_retreat_positions(self):

        total_num_position = 1
        retreat_positions = []
        current_segment = -1
        offset_distance = 1

        current_retrace_length = 0

        while offset_distance < total_num_position + 1:
            length = math.hypot(self.computed_path[current_segment][0] - self.computed_path[current_segment - 1][0],
                                self.computed_path[current_segment][1] - self.computed_path[current_segment - 1][1])

            while offset_distance < current_retrace_length + length and offset_distance < total_num_position + 1:
                proportion = (offset_distance - current_retrace_length) / length
                new_position = list(self.computed_path[current_segment]
                                    + (np.array(self.computed_path[current_segment - 1])
                                       - self.computed_path[current_segment]) * proportion)

                retreat_positions.append(new_position)
                offset_distance += 1

            current_retrace_length += length

        return retreat_positions

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
        red_min_size = 30

        self.computed_path = [centre]
        # Process picture and extract image for analysis.
        image_to_analyse = image

        path_found, new_path = self.calculate_path_from_image(image_to_analyse)
        if path_found:

            # Only add the first part of path as the uneroded path gives errors later on.
            new_path = PathFinder.extract_start_of_path(new_path, length_to_extract=3)
            self.computed_path.extend(new_path)
        else:
            # If we didn't find any part initially throw as something is wrong.
            raise Exception("Did not find any path in first image")

        # Take photos and analyse images until the end is found. Note that if an exception is thrown we catch it and
        # draw whatever path we have found. - This is disabled in debugging. The number of iterations is also capped.
        k = 0
        while k < 200:
            k += 1
            try:
                # Move to new camera position and take photo.
                hardware.plotter.move_camera_to(self.computed_path[-1])
                image = hardware.plotter.take_photo_at(self.computed_path[-1])

                # Analyse photo to check if red is found this also changes any red in the image to white and
                # returns the resulting black and white image.
                red_triangle_found, centre_of_red, bw_image = image_analysis.search_for_red_triangle_near_centre(
                    image, red_min_size)

                if red_triangle_found:
                    # If the red is found convert result to global co-ordinates.
                    global_centre_of_red_list = convert_to_global_coords([centre_of_red],
                                                                         image_analysis_enums.Direction.SOUTH,
                                                                         hardware.plotter._axes.current_location
                                                                         + config.CAMERA_OFFSET,
                                                                         int(image.shape[0] / 2),
                                                                         int(image.shape[1] / 2))

                    # Find the centre of the red trisngle.
                    global_centre_of_red, _ = start_end_detection.find_red_centre(global_centre_of_red_list[0],
                                                                                  min_size=10)

                    # Add this point as the final point in the path.
                    self.computed_path.append(global_centre_of_red)
                    break

                # Process image for analysis.
                image_to_analyse = image_analysis.process_image(bw_image)

                path_found, new_path = self.calculate_path_from_image(image_to_analyse)

                if not path_found:
                    # Check whether the analysis has failed because their was no white in the centre of the eroded
                    #  image. If so retreat along the calculated path until white is found and amend the computed path.
                    centre_moved, image_to_analyse = self.retreat_until_white_in_centre_of_eroded_image(
                        image_to_analyse)

                    # If the centre was moved try analysing the new image.
                    if centre_moved:
                        path_found, new_path = self.calculate_path_from_image(image_to_analyse)

                if not path_found:
                    # If a path was still not found try rotating the image and computing path at different angles.
                    path_found, new_path = self.rotate_to_find_valid_path(image_to_analyse)

                attempts = 0
                while not path_found and attempts < 4 and self.removal_count < 10:
                    attempts += 1

                    # Move back along the path and retry.
                    if not path_found:
                        self.remove_end_of_path(length_to_remove=2)

                        # Move to new camera position and take photo.
                        hardware.plotter.move_camera_to(self.computed_path[-1])
                        image = hardware.plotter.take_photo_at(self.computed_path[-1])

                        # Process image for analysis.
                        image_to_analyse = image_analysis.process_image(image)

                        path_found, new_path = self.calculate_path_from_image(image_to_analyse)

                    if not path_found:
                        # If a path was still not found try rotating the image and computing path at different angles.
                        path_found, new_path = self.rotate_to_find_valid_path(image_to_analyse)

                # All options tried return to draw path.
                if not path_found:
                    break

                self.computed_path.extend(new_path)

                if __debug__:
                    iadebug.save_line_approximation(hardware.plotter.debug_image.debug_image.copy(), self.computed_path,
                                                    False)

            except Exception as e:
                print('Exception: ' + str(e))
                break

        print("k={}".format(k))

    @staticmethod
    def extract_start_of_path(path, length_to_extract):
        """
        This function extracts the start of the path of the given length. A new point is calculated for the final point
        from the line segment it lies on.
        Args:
            path: The path to extract the start from.
            length_to_extract: The length of path to be extracted.

        Returns:
            new_path: The extracted path.

        """
        path_length = 0
        new_path = []

        # Loop over all line segments in the path
        for i in range(len(path) - 1):

            # Calculate segment length.
            segment_length = math.hypot(path[i][0] - path[i + 1][0],
                                        path[i + 1][1] - path[i + 1][1])

            # Compare total path length to desired length. If the total is greater than the desired then this is the
            # segment to stop on. Otherwise continue to the next segment.
            if (path_length + segment_length) > length_to_extract:
                # Calculate the distance along the final segment the final point needs to be.
                distance_along_segment = length_to_extract - path_length

                # Turn the distance into a proportion.
                proportion = distance_along_segment / segment_length

                # Calculate the point.
                new_point = list(np.array(path[i]) * proportion + np.array(path[i + 1]) * (1 - proportion))

                # Take the first i points from the original path.
                new_path = path[:i + 1]

                # Add the final calculated point to the path.
                new_path.append(new_point)

                # Stop as we have now found are path.
                break

            # Add the current segment length to the total path length.
            path_length += segment_length

        # If the path is shorter than the desired distance return the whole path.
        if len(new_path) == 0:
            new_path = path

        return new_path

    def remove_end_of_path(self, length_to_remove):
        """
        This function removes the copmuted path end of the path of the given length. A new point is calculated for the final point
        from the line segment it lies on.
        Args:
            length_to_remove: The length of path to be removed.

        Returns:

        """

        self.removal_count += 1
        if np.linalg.norm(np.array(self.computed_path) - self.path_end_position_at_last_removal) < length_to_remove + 1:
            self.path_end_position_at_last_removal = self.computed_path[-1]
            self.removal_count += 1
        else:
            self.removal_count = 0

        path_length_from_end = 0

        # Loop over all line segments in the path from the back - Note that we dont consider last segment as we dont
        # want to entirely remove path.

        for i in range(len(self.computed_path) - 2, 0, -1):

            # Calculate segment length.
            segment_length = math.hypot(self.computed_path[i][0] - self.computed_path[i + 1][0],
                                        self.computed_path[i + 1][1] - self.computed_path[i + 1][1])

            # Compare total path length from end to desired length. If the total is greater than the desired then
            # this is the segment to stop on. Otherwise continue to the next segment.
            if (path_length_from_end + segment_length) > length_to_remove:
                # Calculate the distance along the final segment the final point needs to be.
                distance_along_segment = length_to_remove - path_length_from_end

                # Turn the distance into a proportion.
                proportion = distance_along_segment / segment_length

                # Calculate the point.
                new_point = list(np.array(self.computed_path[i + 1]) * proportion
                                 + np.array(self.computed_path[i]) * (1 - proportion))

                # Reduce the path to the first i points from the original path.
                self.computed_path = self.computed_path[:i + 1]

                # Add the final calculated point to the path.
                self.computed_path.append(new_point)

                # Stop as we have now found are path.
                break

            # Add the current segment length to the total path length.
            path_length_from_end += segment_length

    def rotate_to_find_valid_path(self, image_to_analyse):

        new_path = []
        for i in range(1, 4):
            # Search for new path. - THIS CANNOT BE DONE WITH UNERODED IMAGE.
            path_found, new_path = self.calculate_path_from_image(image_to_analyse, rotation_deg=i * 20)
            if path_found:
                return True, new_path

        if not path_found:
            return False, new_path

    def retreat_until_white_in_centre_of_eroded_image(self, image_to_analyse):
        """
        If the current image cannot begin to be legally scanned in all directions then retreat along the path until
        a valid image is found.
        Args:
            image_to_analyse: The current image.

        Returns:

        """

        retreated = False
        continue_retreat = True
        DISTANCE_TO_RETREAT = 4

        num_retreats = 0
        while continue_retreat and num_retreats < 4:
            num_retreats += 1
            # Calculate in which directions valid white was found.
            white_found_array = PathFinder.white_found_near_centre(self.search_width, image_to_analyse)

            # Continue retreating if no white was found in any direction.
            for i in range(len(white_found_array)):
                if not white_found_array[i]:
                    retreated = True
                else:
                    continue_retreat = False
                    break

            if not continue_retreat:
                break

            self.remove_end_of_path(DISTANCE_TO_RETREAT)

            # Move to new camera position and take photo.
            hardware.plotter.move_camera_to(self.computed_path[-1])
            image = hardware.plotter.take_photo_at(self.computed_path[-1])

            # Process image for analysis.
            image_to_analyse = image_analysis.process_image(image)

        return retreated, image_to_analyse

    @staticmethod
    def white_found_near_centre(search_width, image_to_analyse):
        """

        Args:
            search_width: Width of area near centre to search.
            image_to_analyse: Image to analyse for white

        Returns:
            array of bools indicating whether white was found.
        """

        search_min_y = int(image_to_analyse.shape[0] / 2 - search_width / 2)
        search_min_x = int(image_to_analyse.shape[1] / 2 - search_width / 2)

        search_max_y = int(image_to_analyse.shape[0] / 2 + search_width / 2)
        search_max_x = int(image_to_analyse.shape[1] / 2 + search_width / 2)

        white_in_first_row_north = sum(image_to_analyse[int(math.floor(image_to_analyse.shape[1] / 2)),
                                       search_min_x:search_max_x]
                                       > image_analysis.white_threshold) > 0
        white_in_first_row_east = sum(image_to_analyse[search_min_y:search_max_y,
                                      int(math.ceil(image_to_analyse.shape[1] / 2))]
                                      > image_analysis.white_threshold) > 0
        white_in_first_row_south = sum(image_to_analyse[int(math.ceil(image_to_analyse.shape[1] / 2)),
                                       search_min_x:search_max_x]
                                       > image_analysis.white_threshold) > 0
        white_in_first_row_west = sum(image_to_analyse[search_min_y:search_max_y,
                                      int(math.floor(image_to_analyse.shape[1] / 2))]
                                      > image_analysis.white_threshold) > 0

        return white_in_first_row_north, white_in_first_row_east, white_in_first_row_south, white_in_first_row_west
