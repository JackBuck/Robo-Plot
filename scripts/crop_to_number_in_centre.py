import argparse

import cv2
import numpy as np

import context
import roboplot.dottodot.number_recognition as number_recognition

# Commandline arguments
parser = argparse.ArgumentParser(description='Crop a dot-to-dot image to just the number closest to the centre.')
parser.add_argument('input_file', type=str, help='the path to the file containing the dot-to-dot image.')
args = parser.parse_args()

# ---  Script body ---

img = number_recognition.read_image(args.input_file)
img = number_recognition._clean_image(img)

# Dilate and Erode to 'clean' the spot (note that this harms the number itself, so we may want to only do this
# temporarily
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
img = cv2.dilate(img, kernel, iterations=1)
img = cv2.erode(img, kernel, iterations=1)

spot_keypoints = number_recognition._extract_spots_from_clean_image(img)

image_centre = np.array(img.shape) / 2
spot_closest_to_centre = min(spot_keypoints, key=lambda s: np.linalg.norm(s.pt - image_centre))

number_recognition._draw_image_with_keypoints(img, [spot_closest_to_centre])
