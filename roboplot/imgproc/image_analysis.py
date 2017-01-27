import numpy as np
import cv2
import enum
import matplotlib
import math
import time


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


        #Orientate image so we are scanning the top half.
        if self._scan_direction == Direction.NORTH:
            self._pixels = self._processed_img
        elif self._scan_direction == Direction.EAST:
            self._pixels = np.rot90(self._processed_img)
        elif self._scan_direction == Direction.SOUTH:
            self._pixels = np.rot90(self._processed_img, 2)
        elif self._scan_direction == Direction.WEST:
            self._pixels = np.rot90(self._processed_img, 3)

        # Create an image with which to display computed values
        if __debug__:
            self._debugimage = cv2.cvtColor(self._pixels, cv2.COLOR_GRAY2RGB)
            debug_pixels = cv2.cvtColor(self._pixels, cv2.COLOR_GRAY2BGR)
            debug_pixels[25, 25] = (0, 200, 0)
            debug_pixels = cv2.resize(debug_pixels, (0, 0), fx=1, fy=1)
            cv2.imshow('Rotated Pixels', debug_pixels)

    def analyse_row(self):

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

        # Analyse each row at a time from the centre moving up the image (backwards in image co-ordinates)
        for rr in range(int(self._height / 2), 0, -1):

            # Determine the indices to average based on the last valid index.
            # Only a proportion of the row is considered this is to filter out any noise/path parts that
            # might be at the edge of the image.
            min_index = int(max(0, average_index_rows[-1] - self._tol + self._width / 2))
            max_index = int(min(self._height, average_index_rows[-1] + self._tol + self._width / 2))
            sub_array = self._pixels[rr, min_index:max_index]

            # Compute the average of the given row portion.
            centroid = ImageAnalyser.compute_weighted_centroid(sub_array)


            # If centroid is valid convert it from image co-ordinates to displacement from centre
            # of the image.

            if centroid != -1:
                next_centroid = min_index + ImageAnalyser.compute_weighted_centroid(sub_array) - self._width / 2
            else:
                next_centroid = -1

            # Only continue if the its the first index or the line as not got too steep. 2 mans cannot go above 45 degrees

            if row_index == 0 or abs(next_centroid - average_index_rows[-1]) < 2:
                average_index_rows.append(next_centroid)
                y_indices.append(row_index)
                last_centroid = Centroid.VALID
                next_camera_position = (-1, -1)
                first_valid_row_found = True

            elif abs(next_centroid - average_index_rows[-1]) >= 2:
                last_centroid = Centroid.INVALID_RANGE
                if last_centroid != Centroid.VALID:
                    # We have 2 invalid entries in a row. Or too big a jump between averages. This means the
                    # approximation should stop.

                    interval = self.find_first_black_row(rr, int(average_index_rows[-1] + self._width / 2))

                    if next_centroid - average_index_rows[-1] < 0:
                        next_scan_direction = self.turn_left()
                        next_camera_position = (int(average_index_rows[-1] - interval / 2), int(row_index + interval / 2))
                    else:
                        next_scan_direction = self.turn_right()
                        next_camera_position = (int(average_index_rows[-1] + interval / 2), int(row_index + interval / 2))
                    break

            else:
                if last_centroid != Centroid.VALID:
                    # We have 2 invalid entries in a row. Or too big a jump between averages. This means the
                    # approximation should stop.

                    if next_centroid - average_index_rows[-1] < 0:
                        next_scan_direction = self.turn_left()
                    else:
                        next_scan_direction = self.turn_right()
                    break

                    last_centroid = Centroid.INVALID_NO_WHITE

            row_index += 1

        if debug:
            self.show_debug_average_row(average_index_rows, y_indices)

        if next_camera_position[1] != -1:
            average_index_rows.append(next_camera_position[0])
            y_indices.append(next_camera_position[1])

        return (average_index_rows, y_indices), next_scan_direction

    def find_first_black_row(self, current_row, column):
        """This function finds the number of rows from the current row until a black pixel is found. """

        pixel = self._pixels[current_row, column]
        count = 0

        while pixel > white_threshold:
            current_row += -1
            pixel = self._pixels[current_row, column]
            count += 1

        return count
