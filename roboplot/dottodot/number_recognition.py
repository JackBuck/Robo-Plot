import PIL.Image as Image
import re
import warnings

import cv2
import numpy as np
import pytesseract


class Number:
    """Represents a number on the dot-to-dot picture."""

    def __init__(self, numeric_value: int, dot_location_yx: tuple):
        """
        Create an instance to represent a number on the dot-to-dot picture.
        
        Args:
            numeric_value (int): the ordinal associated with the dot-to-dot number\n
            dot_location_yx (tuple): a pair (y,x) of floats specifying the location of the dot in the photo
        """
        self.numeric_value = numeric_value
        self.dot_location_yx = dot_location_yx


def read_image(file_path: str) -> np.ndarray:
    """
    Load an image from a supplied file path.

    Args:
        file_path (str): path to the image to return

    Returns:
        np.ndarray: the loaded image
    """
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        return img
    else:
        raise TypeError("Could not open image file: {}".format(file_path))


def recognise_rotated_number(img) -> Number:
    """
    Extract an integer from a potentially rotated image containing text such as '23.'.

    Note that the image must contain a sequence of digits followed by a period '.'.
    The location of the period is used to correctly orient the image before performing text recognition.

    Args:
        img (np.ndarray): the image

    Returns:
        Number: the number detected in the image
    """

    img = _clean_image(img)
    spot = _extract_first_spot_from_clean_image(img)

    if spot is not None:
        current_angle = _estimate_degrees_from_number_centre_to_spot(img, spot)
        desired_angle = -30
        rotated_image = _rotate_image(desired_angle - current_angle, img)
        numeric_value = _recognise_number_in_clean_image(rotated_image)
        spot_location = spot.pt
    else:
        numeric_value = None
        spot_location = None

    return Number(numeric_value, dot_location_yx=spot_location)


def _rotate_image(degrees, img):
    rows, cols = img.shape
    rotation_matrix = cv2.getRotationMatrix2D(center=(cols / 2, rows / 2), angle=degrees, scale=1)
    rotated_image = cv2.warpAffine(img, rotation_matrix, (cols, rows))
    rotated_radians_mod_half_pi = np.deg2rad(degrees % 90)
    new_img_width = img.shape[0] / (np.cos(rotated_radians_mod_half_pi) + np.sin(rotated_radians_mod_half_pi))
    # Crop out the thin remaining border...
    new_img_width = 2 * int((img.shape[0] + new_img_width) / 2 - 1) - img.shape[0]
    rows, cols = rotated_image.shape
    rotated_image, _ = _crop_about(rotated_image, centre=(cols / 2, rows / 2), new_side_length=new_img_width)
    return rotated_image


def _estimate_degrees_from_number_centre_to_spot(img, spot_keypoint):
    spot_x, spot_y = spot_keypoint.pt
    spot_size = spot_keypoint.size
    neighbourhood_of_spot, spot_local_position = _crop_about(img, centre=(spot_y, spot_x),
                                                             new_side_length=20 * spot_size)

    total_intensity = np.sum(255 - neighbourhood_of_spot)
    centroid_y = np.sum(
        np.arange(neighbourhood_of_spot.shape[0]).reshape(-1, 1) * (255 - neighbourhood_of_spot)) / total_intensity
    centroid_x = np.sum(
        np.arange(neighbourhood_of_spot.shape[1]).reshape(1, -1) * (255 - neighbourhood_of_spot)) / total_intensity

    return np.rad2deg(np.arctan2(-(spot_local_position[0] - centroid_y),
                                 spot_local_position[1] - centroid_x))


def _crop_about(img, centre, new_side_length):
    new_side_length = 2 * int(new_side_length / 2)

    cropped_img = img[
                  max(0, centre[0] - new_side_length / 2): centre[0] + new_side_length / 2 + 1,
                  max(0, centre[1] - new_side_length / 2): centre[1] + new_side_length / 2 + 1]

    new_centre = (min(centre[0], new_side_length / 2),
                  min(centre[1], new_side_length / 2))

    return cropped_img, new_centre


def recognise_number(img: np.ndarray) -> Number:
    """
    Extract an integer from an (correctly oriented) image containing text such as '23.'.

    Args:
        img (np.ndarray): a image

    Returns:
        Number: the number detected in the image
    """
    img = _clean_image(img)
    numeric_value = _recognise_number_in_clean_image(img)
    spot = _extract_first_spot_from_clean_image(img)
    spot_location = spot.pt if spot is not None else None
    return Number(numeric_value, dot_location_yx=spot_location)


def _recognise_number_in_clean_image(img) -> int:
    recognised_text = _recognise_number_text(img)
    return _text_to_number(recognised_text)


def _clean_image(img):
    img = cv2.medianBlur(img, ksize=5)
    img = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
    return img


def _recognise_number_text(img: np.ndarray) -> str:
    img = Image.fromarray(img)

    # psm 8 => single word;
    # digits => use the digits config file supplied with the software
    return pytesseract.image_to_string(img, config='-psm 8, digits')


def _text_to_number(recognised_text: str) -> int:
    # Forcing a terminating period helps us to filter out bad results
    match = re.match(r'(\d+)\.$', recognised_text)
    if match is None:
        return None
    else:
        return int(match.group(1))


def _extract_first_spot_from_clean_image(img):
    possible_spots = _extract_spots_from_clean_image(img)
    if len(possible_spots) == 0:
        return None
    else:
        return possible_spots[0]


def _extract_spots_from_clean_image(img):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 20  # The dot in 20pt font has area of about 30
    params.filterByCircularity = True
    params.minCircularity = 0.7
    params.filterByConvexity = True
    params.minConvexity = 0.8
    params.filterByInertia = True
    params.minInertiaRatio = 0.6
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img)
    return keypoints


def _draw_image_with_keypoints(img, keypoints, window_title="Image with keypoints"):
    """An apparently unused method which is actually quite useful when debugging!"""

    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, outImage=np.array([]), color=(0, 0, 255),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow(window_title, img_with_keypoints)
    cv2.waitKey(0)
