#! /usr/bin/env python3

import argparse
import PIL.Image as Image
import re

import cv2
import numpy as np
import pytesseract


def read_image(file_path):
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        return img
    else:
        raise TypeError("Could not open image file: {}".format(file_path))


def clean_image(img):
    img = cv2.medianBlur(img, ksize=5)
    img = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
    return img


def recognise_number_using_rotation_search(img, num_rotations):
    """
    Try recognising the number at a given number of equally spaced rotations of the image.

    Args:
        img: the image on which to perform recognition
        num_rotations: the number of rotations to try

    Returns:
        list: a list of possibilities for the number
    """
    rows, cols = img.shape
    possibilities = []
    for angle in np.linspace(0, 360, num_rotations, endpoint=False):
        rotation_matrix = cv2.getRotationMatrix2D(center=(cols/2, rows/2), angle=angle, scale=1)
        rotated_image = cv2.warpAffine(img, rotation_matrix, (cols, rows))

        # Assume that the image is square and crop it to the new size
        ang = np.deg2rad(angle % 90)
        new_img_width = img.shape[0] / (np.cos(ang) + np.sin(ang))
        # Crop out the thin remaining border...
        new_img_width = 2 * int((img.shape[0] + new_img_width) / 2 - 1) - img.shape[0]
        rotated_image = rotated_image[
                        (img.shape[0] - new_img_width) / 2 : (img.shape[0] + new_img_width) / 2,
                        (img.shape[0] - new_img_width) / 2 : (img.shape[0] + new_img_width) / 2]

        # cv2.imshow("Rotated image", rotated_image)
        # cv2.waitKey(0)

        number_as_text = recognise_number(rotated_image)
        # print(number_as_text)
        number = text_to_number(number_as_text)
        if number is not None:  # and number not in possibilities:
            possibilities.append(number)

    return possibilities


def recognise_number(img):
    img = Image.fromarray(img)

    # psm 8 => single word;
    # digits => use the digits config file supplied with the software
    recognised_text = pytesseract.image_to_string(img, config='-psm 8 digits')
    return recognised_text


def text_to_number(recognised_text: str) -> int:
    match = re.match(r'(\d+)\.$', recognised_text)
    if match is None:
        return None
    else:
        return int(match.group(1))


def extract_spot(img: np.ndarray) -> cv2.KeyPoint:
    params = cv2.SimpleBlobDetector_Params()
    params.minArea = 20  # The dot in 20pt font has area of about 30

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img)
    return keypoints


def draw_image_with_keypoints(img, keypoints, window_title="Image with keypoints"):
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, outImage=np.array([]), color=(0, 0, 255),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow(window_title, img_with_keypoints)
    cv2.waitKey(0)

if __name__ == '__main__':
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Recognise a supplied number.')
    parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
    args = parser.parse_args()

    # Script body
    img = read_image(args.input_file)
    img = clean_image(img)

    recognised_text = recognise_number(img)
    print("Recognised text: {!r}".format(recognised_text), end='\n')
    recognised_number = text_to_number(recognised_text)
    print("Interpreted as: {!r}".format(recognised_number), end='\n\n')

    possibilities_from_rotation_search = recognise_number_using_rotation_search(img, num_rotations=8)
    print("Possible numbers from rotation search: {}".format(", ".join(map(str, possibilities_from_rotation_search))))

    possible_spot_locations = extract_spot(img)
    print("{} possible location(s) found for the spot:".format(len(possible_spot_locations)))
    for keypoint in possible_spot_locations:
        print("size: {}".format(keypoint.size),
              "location: {}".format(keypoint.pt),
              sep=", ")
