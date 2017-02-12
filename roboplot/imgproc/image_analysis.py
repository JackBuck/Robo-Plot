import numpy as np
import cv2
import enum
import os
import math
import time


global white_threshold
white_threshold = 130


class Centroid(enum.IntEnum):
    VALID = 0
    INVALID_RANGE = 1
    INVALID_NO_WHITE = 2


class Direction(enum.IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class ImageAnalyser:
    """This class is holds the information to analyse the path."""

    def __init__(self, image, scan_direction):
        """

        :param image: The image to be analysed
        :param scan_direction: The direction to scan the image in.
        """

        self._scan_direction = scan_direction
        self._original_image = image
        self._height = self._original_image.shape[1]
        self._width = self._original_image.shape[0]

        # Convert image to black and white - we cannot take the photos in black and white as we
        # must first search for the red triangle.
        self._processed_img = cv2.cvtColor(self._original_img, cv2.COLOR_RGB2GRAY)

        # Orientate image so we are scanning the top half.
        if self._scan_direction == Direction.NORTH:
            self._pixels = self._processed_img
        elif self._scan_direction == Direction.EAST:
            self._pixels = np.rot90(self._processed_img)
        elif self._scan_direction == Direction.SOUTH:
            self._pixels = np.rot90(self._processed_img, 2)
        elif self._scan_direction == Direction.WEST:
            self._pixels = np.rot90(self._processed_img, 3)

        # Currently a simple serach width is used based on the size of the image - this is assuming a
        # rough view of 40 x 40 mm^2.
        self._search_width = min(self._original_image.shape[0], self._original_image.shape[1])
        self._search_width /= 2

        # Create an image with which to display computed values
        if __debug__:
            self._debugimage = cv2.cvtColor(self._pixels, cv2.COLOR_GRAY2RGB)
            debug_pixels = cv2.cvtColor(self._pixels, cv2.COLOR_GRAY2BGR)
            debug_pixels[25, 25] = (0, 200, 0)
            debug_pixels = cv2.resize(debug_pixels, (0, 0), fx=1, fy=1)
            cv2.imshow('Rotated Pixels', debug_pixels)

            self._debug_index = 0
            self._debug_line_index = 0

    def analyse_image(self):

        # Get average pixel positions and direction for next photo.
        (indices, next_scan_direction) = self.analyse_row()
        (x_indices, y_indices) = np.array(indices)

        # Approximate the pixels with a line. Start with a line between first and last average pixel.
        pixel_segments = [(0.0, 0.0), (0.0, len(x_indices) - 1)]
        mm_segments = []
        lines = []
        segment_index = 0

        # Max distance allowed between line and average pixel.
        tol = 1

        # Check each calculated segment and check all average pixels are within tolerance of the line.
        # If not split the line and recheck the generated segments.
        while pixel_segments[segment_index][1] < len(x_indices) - 1:
            first_error_exceeding_index = 1
            upper_bound = pixel_segments[segment_index + 1][1]
            while first_error_exceeding_index != -1:

                # Set the start and end of the indices this line covers.
                start_index = int(pixel_segments[segment_index][1])
                end_index = int(upper_bound + 1)

                # Set the start point of the line to the centre 0,0 or the end of the last line calculated.
                if len(lines):
                    if lines[-1][0]:
                        start_point = (int(y_indices[start_index]), int(y_indices[start_index] * lines[-1][0] + lines[-1][1]))
                    else:
                        start_point = (int(y_indices[start_index]), int(x_indices[start_index]))
                else:
                    start_point = (0, 0)

                # Approximate the interval with a line
                y_subset = y_indices[start_index: end_index]
                x_subset = x_indices[start_index: end_index]

                current_line = InterpolateAverages.approximate_with_line(start_point, y_indices[start_index: end_index],
                                                                         x_indices[start_index: end_index])

                # Determine the index at which the distance to the line first exceeds the tolerance. If no index
                # exceeds the tolerance this returns -1.
                first_error_exceeding_index = InterpolateAverages.error_from_line(
                    current_line, y_indices[start_index: end_index], x_indices[start_index: end_index], tol)

                if first_error_exceeding_index != -1:
                    # Shorten the interval to end at the first point the error became too great.
                    # Modify the lowest index to a global index.
                    lowest_index = first_error_exceeding_index + start_index

                    # Split the interval one before the max error this ensures there is a line approximating these
                    # points which is within tolerance of th whole line.
                    upper_bound = lowest_index - 1

                else:
                    # Add this line to the list of lines.
                    segment_x = current_line[0] * upper_bound + current_line[1]
                    pixel_segments.insert(segment_index + 1, (segment_x, upper_bound))

                    transformed_point = self.transform_to_global_system((segment_x, upper_bound))
                    mm_segments.insert(segment_index, transformed_point)
                    lines.append(current_line)

                    # Show current state if debug is set to true.
                    if __debug__:
                        self.DEBUG_show_approximation(lines, pixel_segments, y_indices)

            # Good approximation found for this interval move to next interval.
            segment_index += 1

        # Show current state if debug is set to true and reset indices.
        if __debug__:
            self.DEBUG_show_approximation(lines, pixel_segments, y_indices)
            self._debug_index += 1
            self._debug_line_index = 0

        return mm_segments, next_scan_direction

    def analyse_row(self):
        """

        :return: The indices of the average white pixels found  (centre of the path)
        """

        # Create two lists containing the average index of the white in the given row and the row index of
        # the corresponding row.
        average_index_rows = []
        y_indices = []

        # Always assume the start of the path lies in the centre - this is so the path is not disjoint.
        y_indices.append(0)
        average_index_rows.append(0)

        # Initially assume that the scan direction for the next image is the same as the current direction
        next_scan_direction = self._scan_direction

        # Initialise the state of the last centroid if a valid average could not be found or is too far
        # from the previous average - indicating noise in the image.
        last_centroid = Centroid.VALID

        # Keep track of the current row index - note this counts from the centre up unlike the image co-ords
        row_index = 1
        next_camera_position = (-1, -1)

        # Analyse each row at a time from the centre moving up the image (backwards in image co-ordinates)
        for rr in range(int(self._height / 2), 0, -1):

            # Determine the indices to average based on the last valid index.
            # Only a proportion of the row is considered this is to filter out any noise/path parts that
            # might be at the edge of the image.
            min_index = int(max(0, average_index_rows[-1] - self._search_width + self._width / 2))
            max_index = int(min(self._height, average_index_rows[-1] + self._search_width + self._width / 2))
            sub_array = self._pixels[rr, min_index:max_index]

            # Compute the average of the given row portion.
            centroid = ImageAnalyser.compute_weighted_centroid(sub_array)

            # If centroid is valid convert it from image co-ordinates to displacement from centre
            # of the image.
            if centroid != -1:
                next_centroid = min_index + ImageAnalyser.compute_weighted_centroid(sub_array) - self._width / 2
            else:
                next_centroid = -1

            # Only continue if the its the first index or the line as not got too flat. 2 means cannot go above
            # 45 degrees
            if row_index == 0 or abs(next_centroid - average_index_rows[-1]) < 2:

                # Add result to arrays
                average_index_rows.append(next_centroid)
                y_indices.append(row_index)
                last_centroid = Centroid.VALID

            elif abs(next_centroid - average_index_rows[-1]) >= 2:

                # If the last row was also invalid then we stop as another picture needs to be taken.
                if last_centroid != Centroid.VALID:

                    # We have 2 invalid entries in a row.. This means the approximation should stop.
                    # Find the first central pixel that is black.
                    interval = self.find_first_black_row(rr, int(average_index_rows[-1] + self._width / 2))

                    # Set the next camera position at a 45 degree angle from the current position and half the distance
                    # away in both x and y. This is so that the remaining path in this direction is skipped.

                    #      _____________________
                    #     |
                    #     |      //= Ready for next photo to be taken
                    #     |    //  ______________
                    #     |   ||  |
                    #     |   ||  |
                    #     |   ||  |
                    #     |   ||  |
                    #     |   ||  |
                    #     |   ||  |

                    if next_centroid - average_index_rows[-1] < 0:
                        next_scan_direction = self.turn_left()
                        next_camera_position = (int(average_index_rows[-1] - interval / 2), int(row_index + interval / 2))
                    else:
                        next_scan_direction = self.turn_right()
                        next_camera_position = (int(average_index_rows[-1] + interval / 2), int(row_index + interval / 2))
                    break

                # Flag last centroid as invalid.
                last_centroid = Centroid.INVALID_RANGE

            else:
                if last_centroid != Centroid.VALID:
                    # We have 2 invalid entries in a row. Or too big a jump between averages. This means the
                    # approximation should stop.

                    # NOTE There is a potential to get stuck here if we keep taking photos with no white in
                    # in them.

                    if next_centroid - average_index_rows[-1] < 0:
                        next_scan_direction = self.turn_left()
                    else:
                        next_scan_direction = self.turn_right()
                    break

                    last_centroid = Centroid.INVALID_NO_WHITE

            row_index += 1

        if __debug__:
            self.show_debug_average_row(average_index_rows, y_indices)

        # If we have ended prematurely (and set the next camera position) add this to th list
        # of average pixels found.

        if next_camera_position[1] != -1:
            average_index_rows.append(next_camera_position[0])
            y_indices.append(next_camera_position[1])

        # Return the list of average indices and the scan direction for the next picture taken.
        return (average_index_rows, y_indices), next_scan_direction

    def find_first_black_row(self, current_row, column):
        """
        This function finds the number of rows from the current row until a black pixel is found.
        :param current_row: The index of the current row being analysed.
        :param column: The column index of the last valid index found.
        :return: The number of rows until the next black row.
        """

        # Initially set the pixel to the last valid pixel found.
        pixel = self._pixels[current_row, column]
        count = 0

        # While the pixel is classed as white move up a row (-ve in y)
        global white_threshold
        while pixel > white_threshold:
            current_row += -1
            pixel = self._pixels[current_row, column]
            count += 1

        return count

    def DEBUG_show_approximation(self, lines, segments, y_indices):
        """
        This function shows/saves the stages of the approximation
        :param lines: The equation of the current lines approximating the average rowa
        :param segments: The x indices of the segments between which the lines are used.
        :param y_indices: The y indices of the segments between which the lines are used.
        :return:
        """

        """ Displays the line segments x = my + c on image"""

        # Create copy of image with averages marked on.
        image = self._debugimage.copy()

        # Set centre of image.
        centre = (int(self._width / 2), int(self._height / 2))

        # For each line segment draw a line between the start and end points of the segment and mark the start
        # and end with a circle.

        for current_line in range(0, len(lines)):
            (m, c) = lines[current_line]

            # Compute start co - ordinates of line segment.
            y_start_cart = y_indices[int(segments[current_line][1])]
            x_start_cart = int((y_start_cart * m) + c)

            x_start_cart = int(round(x_start_cart))
            y_start_cart = int(round(y_start_cart))
            (x_start_image, y_start_image) = ImageAnalyser.convert_to_image_coords(
                x_start_cart, y_start_cart, centre, self._scan_direction)

            # Compute end co - ordinate of line segment.
            y_end_cart = int(y_indices[int(segments[current_line + 1][1])])
            x_end_cart = int((y_end_cart * m) + c)

            y_end_cart = int(round(y_end_cart))
            x_end_cart = int(round(x_end_cart))
            (x_end_image, y_end_image) = ImageAnalyser.convert_to_image_coords(
                x_end_cart, y_end_cart, centre, self._scan_direction)

            # Add artifacts to image
            cv2.line(image, (x_start_image, y_start_image), (x_end_image, y_end_image), (255, 10, 10), 2)
            cv2.circle(image, (x_start_image, y_start_image), 3, (255, 10, 10))
            cv2.circle(image, (x_end_image, y_end_image), 3, (255, 10, 10))

        cv2.imshow('LineApproximation', image)
        _curr_dir = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
        _debug_dir = os.path.join(_curr_dir, '..', '..', 'resources')
        cv2.imwrite(_debug_dir + "LineApproximation" + self._debug_index + "_" + self._debug_line_index, image)
        self._debug_line_index += 1

    @staticmethod
    def convert_to_image_coords(x, y, centre, scan_direction):
        """
        This function changes the co-ordinates from the referencing the centre to global pixel
        co-ordinates for the debug image.
        :param x: x co-ord
        :param y: y co-ord
        :param centre: centre of image in the global pixel co-ordinates.
        :param scan_direction: The direction the picture was analysed in (and therefore needs to be rotated
        back appropriately)
        :return:
        """

        if scan_direction == Direction.NORTH:
            x_image = centre[0] + x
            y_image = centre[1] - y
        elif scan_direction == Direction.EAST:
            x_image = centre[1] + y
            y_image = centre[0] + x
        elif scan_direction == Direction.SOUTH:
            x_image = centre[0] - x
            y_image = y + centre[1]
        else:
            x_image = centre[1] - y
            y_image = centre[0] - x

        return x_image, y_image


class InterpolateAverages:
    """This class takes the average row/columns and approximates them with lines
    ready to add to the path"""

    def __init__(self, average_indices):

        self._average_indices = average_indices

    @staticmethod
    def approximate_with_line(start_point, x_indices, y_indices):
        """
        Approximates gradient of line assuming that the line goes through the start point

        Gives gradient y = mx
        """

        x_translated = x_indices  - start_point[0]
        y_translated = y_indices - start_point[1]
        x_translated = x_translated[:, np.newaxis]
        a, _, _, _ = np.linalg.lstsq(x_translated, y_translated)

        c = start_point[1] - start_point[0]*a[0]
        return a[0], c

    @staticmethod
    def error_from_line(line, x_indices, y_indices, max_error):
        """
        Error from line y = mx + c, where line =(m, c) in the inputs.
        This functions fins the first index along the line where the error is greater than the max error bound.
        """

        if line[0]:
            line_normal = np.array([1, -1/line[0]])
            line_normal /= math.sqrt(1+1/(line[0] * line[0]))
        else:
            line_normal = np.array([0, 1])

        origin = np.asarray([0, line[1]])

        # Note that we don't care what the error is to the first 2 indices as we are forcing the start position as
        # we want the line to be continuous.
        for index in range(2, len(x_indices)):

            indices = np.asarray([x_indices[index], y_indices[index]])
            error = InterpolateAverages.error(line_normal, origin, indices)

            if error > max_error:
                return index

        return -1

    @staticmethod
    def error(line_normal, line_origin, indices):

        if indices[0] != -1:
            error = abs(np.dot(line_normal, indices - line_origin))
        else:
            error = 0.0

        return error
