#! /usr/bin/env python3

import argparse
import PIL.Image as Image
import re
import warnings

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


def recognise_rotated_number(img):
    possible_spots = extract_spot(img)

    if len(possible_spots) == 0:
        raise ValueError("Could not find a spot in the image")

    elif len(possible_spots) > 1:
        warnings.warn("Multiple possible spots found - using the first")

    spot_x, spot_y = possible_spots[0].pt
    spot_size = possible_spots[0].size
    neighbourhood_of_spot, spot_local = crop_about(img, centre=(spot_y, spot_x), new_side_length=20 * spot_size)

    total_intensity = np.sum(255 - neighbourhood_of_spot)
    centroid_y = np.sum(
        np.arange(neighbourhood_of_spot.shape[0]).reshape(-1, 1) * (255 - neighbourhood_of_spot)) / total_intensity
    centroid_x = np.sum(
        np.arange(neighbourhood_of_spot.shape[1]).reshape(1, -1) * (255 - neighbourhood_of_spot)) / total_intensity

    # cv2.imshow("Key Points", cv2.drawKeypoints(neighbourhood_of_spot,
    #                                            keypoints=(cv2.KeyPoint(centroid_x, centroid_y, 8.0, 0, 1, 0, 0),
    #                                                       cv2.KeyPoint(spot_local[1], spot_local[0], 8.0, 0, 1, 0, 0)),
    #                                            outImage=np.array([]),
    #                                            color=(0, 0, 255),
    #                                            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS))

    # print("Centroid: ", centroid_x, centroid_y)
    # print("Spot local: ", spot_local[1], spot_local[0])
    current_angle = np.rad2deg(np.arctan2(-(spot_local[0] - centroid_y),
                                          spot_local[1] - centroid_x))
    # print("Current angle: ", current_angle)
    desired_angle = -30  # a guess! You may want to make this more negative to deal with the case of single digit
    # numbers? At any rate, it will be preferable to have the dot lower than the number...

    rows, cols = img.shape
    rotation_matrix = cv2.getRotationMatrix2D(center=(cols / 2, rows / 2), angle=desired_angle - current_angle, scale=1)
    rotated_image = cv2.warpAffine(img, rotation_matrix, (cols, rows))
    # cv2.imshow("Rotated Image", rotated_image)
    # cv2.waitKey(1)

    rotated_radians_mod_half_pi = np.deg2rad((desired_angle - current_angle) % 90)
    new_img_width = img.shape[0] / (np.cos(rotated_radians_mod_half_pi) + np.sin(rotated_radians_mod_half_pi))
    # Crop out the thin remaining border...
    new_img_width = 2 * int((img.shape[0] + new_img_width) / 2 - 1) - img.shape[0]
    rows, cols = rotated_image.shape
    rotated_image, _ = crop_about(rotated_image, centre=(cols / 2, rows / 2), new_side_length=new_img_width)
    # cv2.imshow("Rotated Image", rotated_image)

    number_as_text = recognise_number(rotated_image)
    # print("Recognised text: ", number_as_text)
    number = text_to_number(number_as_text)
    # print("Recognised number: ", number)

    # cv2.waitKey(0)

    return number


def crop_about(img, centre, new_side_length):
    new_side_length = 2 * int(new_side_length / 2)

    cropped_img = img[
                  max(0, centre[0] - new_side_length / 2): centre[0] + new_side_length / 2 + 1,
                  max(0, centre[1] - new_side_length / 2): centre[1] + new_side_length / 2 + 1]

    new_centre = (min(centre[0], new_side_length / 2),
                  min(centre[1], new_side_length / 2))

    return cropped_img, new_centre


def recognise_number(img):
    img = Image.fromarray(img)

    # psm 8 => single word;
    # digits => use the digits config file supplied with the software
    recognised_text = pytesseract.image_to_string(img, config='-psm 8, digits')
    return recognised_text


def text_to_number(recognised_text: str) -> int:
    match = re.match(r'(\d+)\.$', recognised_text)
    if match is None:
        return None
    else:
        return int(match.group(1))


def extract_spot(img: np.ndarray):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 20  # The dot in 20pt font has area of about 30
    params.filterByCircularity = True
    params.minCircularity = 0.8
    params.filterByConvexity = True
    params.minConvexity = 0.8
    params.filterByInertia = True
    params.minInertiaRatio = 0.8

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img)
    return keypoints


def draw_image_with_keypoints(img, keypoints, window_title="Image with keypoints"):
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, outImage=np.array([]), color=(0, 0, 255),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow(window_title, img_with_keypoints)
    cv2.waitKey(0)

# The following bash script shows you some output
# for i in ../Resources/NumberRecognition/*deg.jpg; do echo `basename $i .jpg`; scripts/recognise_number.py $i ;done
# The results are promising where we could find the spot!

if __name__ == '__main__':
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Recognise a supplied number.')
    parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
    args = parser.parse_args()

    # Script body
    img = read_image(args.input_file)
    img = clean_image(img)

    try:
        recognised_number = recognise_rotated_number(img)
    except ValueError:
        recognised_number = "No spot!!"
    print("Recognised number: {!r}".format(recognised_number))

    # recognised_text = recognise_number(img)
    # print("Recognised text: {!r}".format(recognised_text), end='\n')
    # recognised_number = text_to_number(recognised_text)
    # print("Interpreted as: {!r}".format(recognised_number), end='\n\n')
    #
    # possible_spot_locations = extract_spot(img)
    # print("{} possible location(s) found for the spot:".format(len(possible_spot_locations)))
    # for keypoint in possible_spot_locations:
    #     print("size: {}".format(keypoint.size),
    #           "location: {}".format(keypoint.pt),
    #           sep=", ")
