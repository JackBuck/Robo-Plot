#!/usr/bin/env python3

import argparse
import sys

import cv2
import numpy as np

import context
import roboplot.dottodot.number_recognition as number_recognition

# Commandline arguments
parser = argparse.ArgumentParser(description='Crop a dot-to-dot image to just the number closest to the centre.')
parser.add_argument('input_file', type=str, help='the path to the file containing the dot-to-dot image.')
parser.add_argument('-d', '--display-images', action='store_true', help='display intermediate results.')
args = parser.parse_args()

# ---  Script body ---
img = number_recognition.read_image(args.input_file)
img = number_recognition._clean_image(img)

# Dilate and Erode to 'clean' the spot (note that this harms the number itself, so we may want to only do this
# temporarily
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
img_lessnoise = cv2.dilate(img, kernel, iterations=1)
img_lessnoise = cv2.erode(img_lessnoise, kernel, iterations=1)

spot_keypoints = number_recognition._extract_spots_from_clean_image(img_lessnoise)

if len(spot_keypoints) == 0:
    print("No spot found")
    sys.exit(0)

image_centre = np.array(img.shape) / 2
spot_closest_to_centre = min(spot_keypoints, key=lambda s: np.linalg.norm(s.pt - image_centre))

if args.display_images:
    number_recognition._draw_image_with_keypoints(img, [spot_closest_to_centre])

# Find contours
img_inverted = 255 - img
_, contours, _ = cv2.findContours(img_inverted, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)


def draw_image_with_contours(img, contours):
    img_colour = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(img_colour, contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
    cv2.imshow("Image with contours", img_colour)
    cv2.waitKey(0)


# Find the contours associated with the number and spot closest to the centre
grouping_threshold = 10  # The minimum number of pixels between groups of contours


def dist_between_contours(cnt1, cnt2):
    return min([min(np.linalg.norm(cnt1 - pt, axis=2)) for pt in cnt2])


# contours = [cv2.convexHull(c, returnPoints=True) for c in contours]

spot_location_as_contour = np.reshape(spot_closest_to_centre.pt, (-1, 1, 2))
central_contours = [spot_location_as_contour]

still_adding_contours = True
while still_adding_contours:
    still_adding_contours = False

    for i in reversed(range(len(contours))):
        dist_from_central_contours = min([dist_between_contours(contours[i], c) for c in central_contours])
        if dist_from_central_contours < grouping_threshold:
            central_contours.append(contours.pop(i))
            still_adding_contours = True

central_contours = central_contours[1:]

if args.display_images:
    draw_image_with_contours(img, central_contours)


#  Mask the image based on the central contours
mask = np.zeros(img.shape, np.uint8)
cv2.drawContours(mask, central_contours, contourIdx=-1, color=255, thickness=-1)
img[np.where(mask == 0)] = 255

if args.display_images:
    cv2.imshow("Masked image", img)
    cv2.waitKey(0)

# Try to recognise the number
recognised_number = number_recognition.recognise_rotated_number(img)

print("Recognised number: {!r}".format(recognised_number.numeric_value))
print("Probable spot location: {!r}".format(recognised_number.dot_location_yx))
