import numpy as np
import roboplot.imgproc.image_analysis as IP
import cv2


def compute_positions(width, height, photo_size):
    """
    Finds the positions needed for the camera to capture the entire border of the page.
    :param width:
    :param height:
    :param photo_size:
    :return:
    """

    positions = []
    current_path_point = (int(photo_size/2), int(photo_size/2))
    max_x_pos = width - int(photo_size/2)
    max_y_pos = height - int(photo_size/2)

    # Keep y at 0 and move along edge increasing in x.
    while current_path_point[0] < max_y_pos:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0] + photo_size, current_path_point[1])

    current_path_point = (max_y_pos, current_path_point[1])

    # Keep x max and move along edge increasing in y
    while current_path_point[1] < max_x_pos:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0], current_path_point[1] + photo_size)

    current_path_point = (current_path_point[0], max_x_pos)

    # Keep y max and move along edge decreasing in x
    while current_path_point[0] > photo_size/2:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0] - photo_size, current_path_point[1])

    current_path_point = (int(photo_size/2), max_x_pos)

    # Keep x = 0 and move along edge decreasing in y
    while current_path_point[1] > photo_size/2:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0], current_path_point[1] - photo_size)

    return positions
