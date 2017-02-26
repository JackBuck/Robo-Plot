#! /usr/bin/env python3

import argparse
import PIL.Image as Image

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


def recognise_number(img):
    img = Image.fromarray(img)

    # psm 8 => single word;
    # digits => use the digits config file supplied with the software
    recognised_text = pytesseract.image_to_string(img, config='-psm 8 digits')
    return recognised_text


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

    possible_spot_locations = extract_spot(img)
    print("{} possible location(s) found for the spot:".format(len(possible_spot_locations)))
    for keypoint in possible_spot_locations:
        print("size: {}".format(keypoint.size),
              "location: {}".format(keypoint.pt),
              sep=", ")
