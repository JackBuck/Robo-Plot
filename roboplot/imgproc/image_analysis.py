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
import roboplot.imgproc.image_analysis_enums as image_analysis_enums

white_threshold = 130


def compute_centroid_from_row(current_row, last_centroid, search_width):
    """

    Args:
        current_row: The row to be analysed
        last_centroid: The centre of line in the previous row
        search_width: The width of area to be searched.

    Returns:
        centroid: The centre of the line in the current row.
    """

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
    """

    Args:
        lightnesses: The sub_image to average.

    Returns:
        centroid: the centre of the line in the sub_image.
    """
    num_elements = lightnesses.shape

    x = np.arange(num_elements[0])
    is_white = lightnesses > white_threshold
    num_white = sum(is_white)

    if num_white == 0:
        return -1

    flt_centroid = sum(is_white * x) / num_white
    return int(flt_centroid)


def extract_sub_image(processed_image, scan_direction):
    """

    Args:
        image: The image from which to extract relevant sub image
        scan_direction: The direction the path is moving from the centre of the image.

    Returns:
        sub_image: The preprocessed, rotated and

    """

    # Convert image to black and white - we cannot take the photos in black and white as we
    # must first search for the red triangle.

    # Orientate image so we are scanning the bottom half.
    if scan_direction == image_analysis_enums.Direction.NORTH:
        processed_image = np.rot90(processed_image, 2)
    elif scan_direction == image_analysis_enums.Direction.EAST:
        processed_image = np.rot90(processed_image, 3)
    elif scan_direction == image_analysis_enums.Direction.SOUTH:
        processed_image = processed_image
    elif scan_direction == image_analysis_enums.Direction.WEST:
        processed_image = np.rot90(processed_image, 1)

    sub_image = processed_image[int(processed_image.shape[0] / 2):, :]

    # Save sub_image to debug folder if required.
    if __debug__:
        iadebug.save_sub_image(sub_image)

    return sub_image


def process_image(image):
    """

    Args:
        image: The image to process

    Returns:
        sub_image: The rotated and extracted.

    """

    # Convert image to black and white - we cannot take the photos in black and white as we
    # must first search for the red triangle.

    if len(image.shape) == 3:
        processed_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        processed_img = image

    if config.real_hardware:
        num_iterations = 8
    else:
        num_iterations = 8

        processed_img = cv2.GaussianBlur(processed_img, (21, 21), 0)
    _, processed_img = cv2.threshold(processed_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Put a border around the image to stop the edges of the images creating artifacts.
    padded_image = np.zeros((processed_img.shape[0] + 10, processed_img.shape[1] + 10), np.uint8)
    padded_image[5:processed_img.shape[0]+5, 5:processed_img.shape[1]+5] = processed_img

    kernel = np.array([[0, 1, 1, 1, 0],
                       [1, 1, 1, 1, 1],
                       [1, 1, 1, 1, 1],
                       [1, 1, 1, 1, 1],
                       [0, 1, 1, 1, 0]], np.uint8)

    padded_image = cv2.erode(padded_image, kernel, iterations=num_iterations)
    processed_img = padded_image[25:padded_image.shape[0] - 25, 25:padded_image.shape[1] - 25]

    #cv2.imshow('Padded Image', padded_image)
    #cv2.imshow('Processed image', processed_img)
    #cv2.waitKey(0)



    # Debugging code - useful to show the images are being eroded correctly.
    #spacer = processed_img[:, 0:2].copy()
    #spacer.fill(100)
    #combined_image = np.concatenate((processed_img, spacer), axis=1)
    #combined_image = np.concatenate((combined_image, image), axis=1)
    #cv2.imshow('PreProcessed and Processed Image', combined_image)
    #cv2.waitKey(0)

    # Save sub_image to debug folder if required.
    if __debug__:
        iadebug.save_processed_image(processed_img)

    return processed_img


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
    indices, turn_to_next_scan = analyse_rows(image, search_width, is_rotated=False)

    if __debug__:
        debug_image = iadebug.save_average_rows(image, indices, is_rotated=False)
    else:
        debug_image = None

    if len(indices) == 0:
        return [[-1, -1], [-1, -1]], turn_to_next_scan

    pixel_segments = approximate_path(indices)

    # Show current state if debug is set to true.
    if __debug__:
        iadebug.save_line_approximation(debug_image, pixel_segments, is_rotated=False)

    # If we have ended prematurely try continuing the scan by rotating the image by +/-60.
    if (len(indices) < image.shape[0] - 20) \
            and (turn_to_next_scan is not image_analysis_enums.Turning.STRAIGHT) \
            and (turn_to_next_scan is not image_analysis_enums.Turning.INVALID):

        if turn_to_next_scan is image_analysis_enums.Turning.LEFT:
            angle_rad = np.deg2rad(-60)
        else:
            angle_rad = np.deg2rad(60)

        # Create rotated sub_image to analyse
        sub_image = create_rotated_sub_image(image, indices[-1], search_width, angle_rad)

        # Analyse sub image
        rotated_indices, rotated_turn_to_next_scan = analyse_rows(sub_image, search_width, is_rotated=True)
        if __debug__:
            debug_sub_image = iadebug.save_average_rows(sub_image, rotated_indices, is_rotated=True)
        else:
            debug_sub_image = None

        # Compute approximate lines on sub_image

        if len(rotated_indices) != 0:
            rotated_pixel_segments = approximate_path(rotated_indices)

            # Show current state if debug is set to true and reset indices.
            if __debug__:
                iadebug.save_line_approximation(debug_sub_image, rotated_pixel_segments, is_rotated=True)

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
        iadebug.save_line_approximation(debug_image, pixel_segments,is_rotated=False)

    # If there was not enough path in the photo try another orientation.
    if turn_to_next_scan is image_analysis_enums.Turning.INVALID:
        return [[-1, -1], [-1, -1]], turn_to_next_scan

    return pixel_segments, turn_to_next_scan


def analyse_rows(pixels, search_width, is_rotated):
    """

    Args:
        pixels: Image to be analysed
        search_width: The width around the path to be analysed.
        is_rotated: Whether the image being analysed has been rotated.

    Returns:
        The indices of the average white pixels found  (centre of the path) and the direction to turn to continue
        analysing the path.

    """
    # Create two lists containing the average index of the white in the given row and the row index of
    # the corresponding row.
    indices = []

    # Always assume the start of the path lies in the centre - this is so the path is not disjoint.
    indices.append([0, int(pixels.shape[1] / 2)])

    # Initially assume that the scan direction for the next image is the same as the current direction
    turn_to_next_scan = image_analysis_enums.Turning.STRAIGHT

    # Initialise the state of the last centroid if a valid average could not be found or is too far
    # from the previous average - indicating noise in the image.
    last_centroid_validity = image_analysis_enums.Centroid.VALID

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
            last_centroid_validity = image_analysis_enums.Centroid.VALID

        elif abs(next_centroid - indices[-1][1]) >= 2 and next_centroid != -1:
            # Invalid result - too much of a gap created.
            # If the last row was also invalid then we stop as another picture needs to be taken.
            if last_centroid_validity != image_analysis_enums.Centroid.VALID:
                if next_centroid - indices[-1][1] < 0:
                    turn_to_next_scan = image_analysis_enums.Turning.RIGHT
                else:
                    turn_to_next_scan = image_analysis_enums.Turning.LEFT
                break

            # Flag last centroid as invalid.
            last_centroid_validity = image_analysis_enums.Centroid.INVALID_RANGE

        else:
            # We have an invalid row because no white was found.
            if last_centroid_validity != image_analysis_enums.Centroid.VALID:
                # We have 2 invalid entries in a row. Or too big a jump between averages. This means the
                # approximation should stop.

                # NOTE There is a potential to get stuck here if we keep taking photos with no white in
                # in them.

                if next_centroid - indices[-1][1] < 0:
                    turn_to_next_scan = image_analysis_enums.Turning.LEFT
                else:
                    turn_to_next_scan = image_analysis_enums.Turning.RIGHT
                break

            last_centroid_validity = image_analysis_enums.Centroid.INVALID_NO_WHITE

    # Return the list of average indices and the scan direction for the next picture taken.

    min_number = max(10, int(pixels.shape[0]/50))
    if len(indices) < min_number and last_centroid_validity is image_analysis_enums.Centroid.INVALID_NO_WHITE:
        turn_to_next_scan = image_analysis_enums.Turning.INVALID

        # If we end in black remove the last min number of indices
        indices = indices[:-min_number+1]

    return indices, turn_to_next_scan


def approximate_with_line(start_point, end_point):
    """
    Calculates the line between the first and last point in the indices list.
    Args:
        start_point: Start of the line.
        end_point: Start of the line.

    Returns:
        The gradient and constant of the line.
    """

    gradient = (end_point[1] - start_point[1])/(end_point[0] - start_point[0])
    c = start_point[1] - gradient*start_point[0]
    return gradient, c


def error_from_line(line, indices, max_error):
    """
        This functions finds the first index along the line where the error is greater than the max error bound.
    Args:
        line: The coefficients of the line approximation.
        indices: The indices being approximated.
        max_error: The max error allowed from the line

    Returns:
        The indices of the point that first breaks the maximum error.
    """
    if abs(line[0]):
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

    pixel_segments = [pixel_indices[0]]
    segment_index = 0

    # Max distance allowed between line and average pixel.
    tol = 2

    # Start by trying to approximate the indices with a single line through the first and last average indices.
    line_start_index = 0

    while line_start_index < len(pixel_indices) - 1:
        # Record the first index in the interval of interest (line start - line end) that violates the tolerance.
        first_local_error_exceeding_index = 1

        # Start by trying to end the next line segment with the final index.
        candidate_line_end_index = len(pixel_indices)-1

        # Keep reducing the index of the candidate line end until all average points lie within the tolerance.
        while first_local_error_exceeding_index != -1:

            # Approximate the interval with a line
            subset = pixel_indices[line_start_index: candidate_line_end_index]

            current_line = approximate_with_line(pixel_indices[line_start_index], pixel_indices[candidate_line_end_index])

            # Determine the index at which the distance to the line first exceeds the tolerance. If no index
            # exceeds the tolerance this returns -1.
            first_local_error_exceeding_index = error_from_line(current_line, subset, tol)

            if first_local_error_exceeding_index != -1:
                # Shorten the interval to end at maximum of the first point the error became too great or
                # half the interval.
                # Modify the lowest index to a global index.
                
                half_interval_index = line_start_index + int((candidate_line_end_index - line_start_index)/2)
                first_error_index = line_start_index + first_local_error_exceeding_index
                
                candidate_line_end_index = max(half_interval_index, first_error_index)
            else:
                # Add this line to the list of lines. (y , x)

                pixel_segments.insert(segment_index + 1, pixel_indices[candidate_line_end_index])
                line_start_index = candidate_line_end_index

        # Good approximation found for this interval move to next interval.
        segment_index += 1

    return pixel_segments


def create_rotated_sub_image(image, centre, search_width, angle_rad):
    # Rotation transform requires x then y.
    M = cv2.getRotationMatrix2D((centre[1], centre[0]), np.rad2deg(angle_rad), 1.0)

    w = image.shape[1]
    h = centre[0] + int((image.shape[0] - centre[0]) * abs(math.sin(angle_rad)))
    rotated = cv2.warpAffine(image, M, (w, h))

    # Centre the last white centroid into the centre of the image.
    half_sub_image_width = int(min(min(search_width, centre[1]),
                                   min(rotated.shape[1] - centre[1], search_width)))

    sub_image = rotated[centre[0]:,
                centre[1] - half_sub_image_width: centre[1] + half_sub_image_width]

    return sub_image


def search_for_red_triangle_near_centre(photo, min_size):
    mid_point = int(photo.shape[0] / 2)
    half_restricted_size = 30

    hsv_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
    centre_array = cd.detect_red(hsv_photo, min_size, change_to_white=False)

    for centre in centre_array:
        if (mid_point - half_restricted_size < centre[0] < mid_point + half_restricted_size)\
                and (mid_point - half_restricted_size < centre[1] < mid_point + half_restricted_size):
            return True, [centre[0], centre[1]], hsv_photo[:, :, 2]

    return False, None, hsv_photo[:, :, 2]


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
        return image_analysis_enums.Direction.NORTH

    if max_num_pixels == east_whiteness_total:
        return image_analysis_enums.Direction.EAST

    if max_num_pixels == south_whiteness_total:
        return image_analysis_enums.Direction.SOUTH

    if max_num_pixels == west_whiteness_total:
        return image_analysis_enums.Direction.WEST


def analyse_candidate_path(computed_path, candidate_path):

    # Approximate length of path generated by computing distance between first and last point in candidate edge.

    length = distance_point_to_point(candidate_path[0], candidate_path[-1])

    for j in range(1, len(candidate_path)):

        distance_to_centre = distance_point_to_point(candidate_path[j], candidate_path[0])

        for i in range(len(computed_path)-1, 0, -1):
            distance_to_computed_path = distance_point_to_line_segment(np.array(candidate_path[j]),
                                                                       np.array(computed_path[i-1]),
                                                                       np.array(computed_path[i]))

            # If at any point the path gets within half a path width of a previously computed point. And is also closer
            # to that point than it is to the computed centre mark this direction as invalid.

            if distance_to_computed_path < 2.5 and distance_to_centre > 5: # This is based on a minimum angle of 30
                return length, False

            # If the path gets sufficiently far from the previous path - same to assume that we have not done a u
            if distance_to_computed_path > 40:
                break

    return length, True


def distance_point_to_point(pointA, pointB):
    return math.hypot(pointA[0] - pointB[0], pointA[1] - pointB[1])

def distance_point_to_line_segment(point, line_seg_start, line_seg_end):
    v = line_seg_end - line_seg_start
    w = point - line_seg_start

    # point is before start of line, closest point is start point.
    c1 = np.dot(w, v)
    if c1 <= 0:
        return distance_point_to_point(point, line_seg_start)

    # point is after end of line, closest point is end point.
    c2 = np.dot(v, v)
    if c2 <= c1:
        return distance_point_to_point(point, line_seg_end)

    # Closest point is on line segment calculate point and then calculate distance.
    b = c1 / c2
    closest_point_on_line = line_seg_start + b * v
    return distance_point_to_point(point, closest_point_on_line)


def compute_next_direction_feelers(image, processed_image, current_direction):
    # This has drawbacks as mention by JB.

    (north_feeler_length, east_feeler_length, south_feeler_length, west_feeler_length) = compute_feeler_lengths(processed_image, current_direction)

    max_feeler_length = max(north_feeler_length, east_feeler_length, south_feeler_length, west_feeler_length)

    # If no feelers were found in the processed image use the raw image to find the direction.
    if max_feeler_length == 0:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        (north_feeler_length, east_feeler_length, south_feeler_length, west_feeler_length) = compute_feeler_lengths(
            image, current_direction)
        max_feeler_length = max(north_feeler_length, east_feeler_length, south_feeler_length, west_feeler_length)

    if max_feeler_length == north_feeler_length:
        return image_analysis_enums.Direction.NORTH
    elif max_feeler_length == east_feeler_length:
        return image_analysis_enums.Direction.EAST
    elif max_feeler_length == south_feeler_length:
        return image_analysis_enums.Direction.SOUTH
    elif max_feeler_length == west_feeler_length:
        return image_analysis_enums.Direction.WEST


def compute_feeler_lengths(processed_image, current_direction):

    north_feeler_length = 0
    east_feeler_length = 0
    west_feeler_length = 0
    south_feeler_length = 0

    if current_direction is not image_analysis_enums.Direction.NORTH:
        y_index = int(processed_image.shape[0] / 2)
        x_index = int(processed_image.shape[1] / 2)
        current_pixel = processed_image[y_index, x_index]

        while current_pixel > white_threshold and y_index < processed_image.shape[0] - 1:
            y_index += 1
            south_feeler_length += 1
            current_pixel = processed_image[y_index, x_index]

    if current_direction is not image_analysis_enums.Direction.EAST:
        y_index = int(processed_image.shape[0] / 2)
        x_index = int(processed_image.shape[1] / 2)
        current_pixel = processed_image[y_index, x_index]

        while current_pixel > white_threshold and x_index > 0:
            x_index -= 1
            west_feeler_length += 1
            current_pixel = processed_image[y_index, x_index]

    if current_direction is not image_analysis_enums.Direction.SOUTH:
        y_index = int(processed_image.shape[0] / 2)
        x_index = int(processed_image.shape[1] / 2)
        current_pixel = processed_image[y_index, x_index]

        while current_pixel > white_threshold and y_index > 0:
            y_index -= 1
            north_feeler_length += 1
            current_pixel = processed_image[y_index, x_index]

    if current_direction is not image_analysis_enums.Direction.WEST:
        y_index = int(processed_image.shape[0] / 2)
        x_index = int(processed_image.shape[1] / 2)
        current_pixel = processed_image[y_index, x_index]

        while current_pixel > white_threshold and x_index < processed_image.shape[1] - 1:
            x_index += 1
            east_feeler_length += 1
            current_pixel = processed_image[y_index, x_index]

    return (north_feeler_length, east_feeler_length, south_feeler_length, west_feeler_length)


## Legacy ##
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

