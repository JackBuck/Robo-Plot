import enum
import os
import math
import datetime
import operator

import numpy as np
import cv2

import roboplot.config as config
import roboplot.imgproc.image_analysis_debug as iadebug
import roboplot.imgproc.colour_detection as cd

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


def turn_left(current_direction):
    direction_array = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    direction_index = (current_direction - 1) % 4
    return direction_array[direction_index]


def turn_right(current_direction):
    direction_array = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    direction_index = (current_direction + 1) % 4
    return direction_array[direction_index]


class Turning(enum.IntEnum):
    LEFT = 0
    STRAIGHT = 1
    RIGHT = 2


def compute_centroid_from_row(current_row, last_centroid, search_width):

    # If the centroid from the last row is black in this row examine the width of the search area.
    if current_row[last_centroid] < 130:
        min_index = int(max(0, last_centroid - search_width / 2))
        max_index = int(min(current_row.shape[0], last_centroid + search_width / 2))

    # Otherwise grow the search area at either end until they hit black pixels. If the side of the
    # image is hit return an incorrect centroid.
    else:
        min_index = last_centroid - 1
        while min_index > 0 and current_row[min_index] > 130:
            min_index -= 1

        max_index = last_centroid + 1
        while max_index < current_row.shape[0] and current_row[max_index] > 130:
            max_index += 1

    image_to_analyse = current_row[min_index:max_index]

    # temp_image = current_row.copy()
    # temp_image = cv2.cvtColor(temp_image, cv2.COLOR_GRAY2BGR)
    # temp_image[min_index] = (255, 100, 200)
    # temp_image[max_index] = (255, 100, 200)
    # temp_image = np.tile(temp_image, (25, 1))
    # temp_image = np.rot90(temp_image, 1)
    # cv2.imshow('Row', cv2.resize(temp_image, (0, 0), fx=3, fy=3))
    #cv2.waitKey(0)

    # Compute the average of the given row portion.

    sub_image_centroid = compute_centroid(image_to_analyse)
    if sub_image_centroid == -1:
        return -1
    else:
        return sub_image_centroid + min_index


def compute_centroid(lightnesses):
    num_elements = lightnesses.shape

    x = np.arange(num_elements[0])
    is_white = lightnesses > white_threshold
    num_white = sum(is_white)
    weighted = np.multiply(is_white, x)

    if num_white == 0:
        return -1

    flt_centroid = sum(is_white * x) / num_white
    return int(flt_centroid)


def process_and_extract_sub_image(image, scan_direction):
    """

    Args:
        image: The image from which to extract relevant sub image
        scan_direction: The direction the path is moving from the centre of the image.

    Returns:
        sub_image: The preprocessed, rotated and

    """

    # Convert image to black and white - we cannot take the photos in black and white as we
    # must first search for the red triangle.

    # Assuming the rotations below are quicker by converting to gray scale first if not already gray
    if len(image.shape) == 3:
        processed_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        processed_img = image



    # Orientate image so we are scanning the bottom half.
    if scan_direction == Direction.NORTH:
        pixels = np.rot90(processed_img, 2)
    elif scan_direction == Direction.EAST:
        pixels = np.rot90(processed_img, 3)
    elif scan_direction == Direction.SOUTH:
        pixels = processed_img
    elif scan_direction == Direction.WEST:
        pixels = np.rot90(processed_img, 1)

    pixels = cv2.GaussianBlur(pixels, (21, 21), 0)
    _, pixels = cv2.threshold(pixels, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.array([[0, 1, 1, 1, 0],
                       [1, 1, 1, 1, 1],
                       [1, 1, 1, 1, 1],
                       [1, 1, 1, 1, 1],
                       [0, 1, 1, 1, 0]], np.uint8)

    pixels = cv2.erode(pixels, kernel, iterations=10)

    # Debugging code - useful to show the images are being eroded correctly.
    #spacer = processed_img[:, 0:2].copy()
    #spacer.fill(100)
    #combined_image = np.concatenate((processed_img, spacer), axis=1)
    #combined_image = np.concatenate((combined_image, pixels), axis=1)
    #cv2.imshow('PreProcessed and Processed Image', combined_image)
    #cv2.waitKey(0)

    sub_image = pixels[int(pixels.shape[0] / 2):, :]

    # Save sub_image to debug folder if required.
    if __debug__:
        cv2.imwrite(os.path.join(config.debug_output_folder,
                                 datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f") + 'aa_sub_image' + '.jpg'),
                    sub_image)

    return sub_image


def compute_pixel_path(image, search_width):
    """

    Args:
        image: The image to compute a pixel path for.
        search_width: The width of area around the central pixel to be searched.

    Returns:
        pixel_segements: An array containing the pixel co-ordinates of the line ends.
        turn_to_next_scan: The direction the path is turning in at the end of this photo.

    """

    # Get average pixel positions and next path direction for photo.
    indices, turn_to_next_scan = analyse_rows(image, search_width, False)

    if __debug__:
        debug_image = iadebug.save_average_rows(image, indices, False)
    else:
        debug_image = None

    pixel_segments = approximate_path(indices)

    # Show current state if debug is set to true.
    if __debug__:
        iadebug.save_line_approximation(debug_image, pixel_segments, False)

    # If we have ended prematurely try continuing the scan by rotating the image by +/-60.
    if (len(indices) < image.shape[0]) and (turn_to_next_scan is not Turning.STRAIGHT):

        if turn_to_next_scan is Turning.LEFT:
            angle_rad = np.deg2rad(-60)
        else:
            angle_rad = np.deg2rad(60)

        # Create rotated sub_image to analyse
        sub_image = create_rotated_sub_image(image, indices[-1], search_width, angle_rad)

        # Analyse sub image
        rotated_indices, rotated_turn_to_next_scan = analyse_rows(sub_image, search_width, True)
        if __debug__:
            debug_sub_image = iadebug.save_average_rows(sub_image, rotated_indices, True)
        else:
            debug_sub_image = None

        # Check that the turns do not disagree. If neither are straight and the disagree compromise on
        # straight.
        if turn_to_next_scan is not Turning.STRAIGHT \
                and rotated_turn_to_next_scan is not Turning.STRAIGHT \
                and turn_to_next_scan is not rotated_turn_to_next_scan:
            turn_to_next_scan = Turning.STRAIGHT

        # Compute approximate lines on sub_image
        rotated_pixel_segments = approximate_path(rotated_indices)

        # Show current state if debug is set to true and reset indices.
        if __debug__:
            iadebug.save_line_approximation(debug_sub_image, rotated_pixel_segments, True)

            # Rotate line indices back.
            extra_pixel_segments = [list(map(operator.add,
                                             (int(pixel_segments[-1][0]),
                                              int(pixel_segments[-1][1] - sub_image.shape[1] / 2)),
                                             rotate(rotated_pixel_segments[0], point, -angle_rad)))
                                    for point in rotated_pixel_segments]
        # Add segments to list.
        pixel_segments += extra_pixel_segments

    if __debug__:
        debug_image = iadebug.create_debug_image(image)
        iadebug.save_line_approximation(debug_image, pixel_segments, False)

    return pixel_segments, turn_to_next_scan


def analyse_rows(pixels, search_width, is_rotated):
    """

    Args:
        pixels: Image to be analysed
        search_width: The width around the path to be analysed.

    Returns: The indices of the average white pixels found  (centre of the path) and the
                direction to turn to continue analysing the path.

    """
    # Create two lists containing the average index of the white in the given row and the row index of
    # the corresponding row.
    indices = []

    # Always assume the start of the path lies in the centre - this is so the path is not disjoint.
    indices.append([0, int(pixels.shape[1] / 2)])

    # Initially assume that the scan direction for the next image is the same as the current direction
    turn_to_next_scan = Turning.STRAIGHT

    # Initialise the state of the last centroid if a valid average could not be found or is too far
    # from the previous average - indicating noise in the image.
    last_centroid = Centroid.VALID


    # Analyse each row at a time from the top moving down the image.

    for rr in range(1, pixels.shape[0]):

        # Determine the indices to average based on the last valid index.
        # Only a proportion of the row is considered this is to filter out any noise/path parts that
        # might be at the edge of the image.

        next_centroid = compute_centroid_from_row(pixels[rr, :], indices[-1][1], search_width)

        # EXPERIMENTAL -can cause rotations to not give much.
        if is_rotated \
                and rr > pixels.shape[0] - 25 \
                and (next_centroid < 25 or next_centroid > pixels.shape[1] - 25):
            # if next_centroid - indices[-1][1] < 0:
            #     turn_to_next_scan = Turning.RIGHT
            # else:
            #     turn_to_next_scan = Turning.LEFT
            break

        # Only continue if the its the first index or the line as not got too flat. 2 means cannot go above
        # 45 degrees.  If we are on the first row abandon the averaging if the centroid found is black in
        # the first row as this implied the picture is not ideal.
        if (rr == 1 and pixels[0, next_centroid] > 130) or abs(next_centroid - indices[-1][1]) < 2:
            # Valid result, add result to arrays
            indices.append([rr, next_centroid])
            last_centroid = Centroid.VALID

        elif abs(next_centroid - indices[-1][1]) >= 2:
            # Invalid result - too much of a gap created.
            # If the last row was also invalid then we stop as another picture needs to be taken.
            if last_centroid != Centroid.VALID:
                if next_centroid - indices[-1][1] < 0:
                    turn_to_next_scan = Turning.RIGHT
                else:
                    turn_to_next_scan = Turning.LEFT
                break

            # Flag last centroid as invalid.
            last_centroid = Centroid.INVALID_RANGE

        else:
            # We have an invalid row because no white was found.
            if last_centroid != Centroid.VALID:
                # We have 2 invalid entries in a row. Or too big a jump between averages. This means the
                # approximation should stop.

                # NOTE There is a potential to get stuck here if we keep taking photos with no white in
                # in them.

                if next_centroid - indices[-1][1] < 0:
                    turn_to_next_scan = Turning.LEFT
                else:
                    turn_to_next_scan = Turning.RIGHT
                break

                last_centroid = Centroid.INVALID_NO_WHITE

    # Return the list of average indices and the scan direction for the next picture taken.
    return indices, turn_to_next_scan

def find_first_black_row(image, current_row, column):
    """
    This function finds the number of rows from the current row until a black pixel is found.
    :param current_row: The index of the current row being analysed.
    :param column: The column index of the last valid index found.
    :return: The number of rows until the next black row.
    """

    # Initially set the pixel to the last valid pixel found.
    pixel = image[current_row, column]
    count = 0

    # While the pixel is classed as white move down a row
    while pixel > white_threshold and current_row < image.shape[0] - 1:
        current_row += 1
        pixel = image[current_row, column]
        count += 1

    return count


def approximate_with_line(indices):
    """
    Approximates gradient of line assuming that the line goes through the start point

    Gives gradient y = mx
    """

    # Indices are ordered y, x in list.
    x_translated = np.array(indices)[:, 1] - indices[0][1]
    y_translated = np.array(indices)[:, 0] - indices[0][0]
    y_translated = y_translated[:, np.newaxis]
    a, _, _, _ = np.linalg.lstsq(y_translated, x_translated)

    c = indices[0][1] - indices[0][0] * a[0]
    return a[0], c


def error_from_line(line, indices, max_error):
    """
    Error from line y = mx + c, where line = (m, c) in the inputs.
    This functions finds the first index along the line where the error is greater than the max error bound.
    """
    if line[0]:
        line_normal = np.array([1, -1 / line[0]])
        line_normal /= math.sqrt(1 + 1 / (line[0] * line[0]))
    else:
        line_normal = np.array([0, 1])

    origin = np.asarray([0, line[1]])

    # Note that we don't care what the error is to the first 2 indices as we are forcing the start position as
    # we want the line to be continuous.
    for index in range(2, len(indices)):
        error = compute_error(line_normal, origin, indices[index])
        if error > max_error:
            return index
    return -1


def compute_error(line_normal, line_origin, indices):
    if indices[0] != -1:
        error = abs(np.dot(line_normal, indices - line_origin))
    else:
        error = 0.0
    return error


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)

    qx = ox + cos_angle * (px - ox) - sin_angle * (py - oy)
    qy = oy + sin_angle * (px - ox) + cos_angle * (py - oy)
    return [int(qx), int(qy)]


def approximate_path(pixel_indices):
    # Approximate the pixels with a line. Start with a line between first and last average pixel.
    # Pixels in the segment index are ordered y, x

    pixel_segments = [pixel_indices[0], pixel_indices[-1]]
    segment_index = 0

    # Max distance allowed between line and average pixel.
    tol = 3

    # Check each calculated segment and check all average pixels are within tolerance of the line.
    # If not split the line and recheck the generated segments.
    while pixel_segments[segment_index][0] < pixel_indices[-1][0] - 1:
        first_error_exceeding_index = 1
        max_interval_index = pixel_segments[segment_index + 1][0]
        while first_error_exceeding_index != -1:

            # Set the start and end of the indices this line covers.
            start_index = int(math.ceil(pixel_segments[segment_index][0] - 0.5))
            end_index = int(math.ceil(max_interval_index))

            # Approximate the interval with a line
            subset = pixel_indices[start_index: end_index]

            current_line = approximate_with_line(subset)

            # Determine the index at which the distance to the line first exceeds the tolerance. If no index
            # exceeds the tolerance this returns -1.
            first_error_exceeding_index = error_from_line(current_line, subset, tol)

            if first_error_exceeding_index != -1:
                # Shorten the interval to end at the first point the error became too great.
                # Modify the lowest index to a global index.
                max_interval_index = first_error_exceeding_index + start_index - 1

            else:
                # Add this line to the list of lines. (y , x)

                # Can use computed point but this would require this to be added to the list of indices
                # considered for the next line to remove kinks.
                # new_point = [pixel_indices[end_index][0], int(pixel_indices[end_index][0]*current_line[0] + current_line[1])]

                # Currently simply use the last index as can only be tolerance out.
                pixel_segments.insert(segment_index + 1, pixel_indices[end_index])

        # Good approximation found for this interval move to next interval.
        segment_index += 1

    return pixel_segments


def create_rotated_sub_image(image, centre, search_width, angle_rad):
    # Rotation transform requires x then y.
    M = cv2.getRotationMatrix2D((centre[1], centre[0]), np.rad2deg(angle_rad), 1.0)

    w = image.shape[1]

    h = centre[0] + int((image.shape[0] - centre[0]) * abs(math.sin(angle_rad)))
    #int(centre[0] + (w / 2 - abs(centre[1] - w / 2)) * abs(math.sin(angle_rad)))

    rotated = cv2.warpAffine(image, M, (w, h))

    # Centre the last white centroid into the centre of the image.
    half_sub_image_width = int(min(min(search_width, centre[1]),
                                   min(rotated.shape[1] - centre[1], search_width)))

    sub_image = rotated[centre[0]:,
                centre[1] - half_sub_image_width: centre[1] + half_sub_image_width]

    return sub_image


def search_for_red_triangle_near_centre(photo, min_size):
    mid_point = int(photo.shape[0] / 2)
    restricted_image = photo[mid_point - 20:mid_point + 20, mid_point - 20:mid_point + 20]
    hsv_restricted_image = cv2.cvtColor(restricted_image, cv2.COLOR_BGR2HSV)
    (cX, cY) = cd.detect_red(hsv_restricted_image, min_size, False)

    if cX == -1:
        return False, [cX, cY]
    else:
        return True, [mid_point - 20 + cX, mid_point - 20 + cY]


def find_start_direction(img):
    """
    This function takes an image and determine which direction the path leaves the centre from.
    Note in cases where the start of the path is at an angle (see northnortheast and eastnortheast
    test cases) the result is sub optimal however the method should still be able to cope with 
    these systems by recognising that the path needs to be rotated. If this is not the case 
    this method will need to be revisited.
    
    Args:
        img: The image whose centre is at the centre of the green triangle which has now been made
             white.

    Returns:
        enum.IntEnum orientation.
    """

    # Extract centre of the image.

    img_height = img.shape[0]
    img_width = img.shape[1]

    sub_array = img[int(img_height / 3):int(2 * img_height / 3), int(img_width / 3):int(2 * img_width / 3)]

    # Determine which orientation contains the most white pixels.
    # North
    north_sub_array = sub_array[:int(sub_array.shape[0] / 2), :]
    north_whiteness_total = north_sub_array.sum()

    # East
    east_sub_array = sub_array[:, int(sub_array.shape[1] / 2):]
    east_whiteness_total = east_sub_array.sum()

    # South
    south_sub_array = sub_array[int(sub_array.shape[0] / 2):, :]
    south_whiteness_total = south_sub_array.sum()

    # West
    west_sub_array = sub_array[:, :int(sub_array.shape[1] / 2)]
    west_whiteness_total = west_sub_array.sum()

    max_num_pixels = max(north_whiteness_total, east_whiteness_total,
                         south_whiteness_total, west_whiteness_total)

    if max_num_pixels == north_whiteness_total:
        return Direction.NORTH

    if max_num_pixels == east_whiteness_total:
        return Direction.EAST

    if max_num_pixels == south_whiteness_total:
        return Direction.SOUTH

    if max_num_pixels == west_whiteness_total:
        return Direction.WEST
