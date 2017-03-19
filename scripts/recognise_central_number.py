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

spot_closest_to_centre = number_recognition._extract_spot_closest_to_centre_from_clean_image(img)

if spot_closest_to_centre is None:
    print("No spot found")
    sys.exit(0)

if args.display_images:
    number_recognition.draw_image_with_keypoints(img, [spot_closest_to_centre])

central_contours = number_recognition._extract_contours_close_to(img, spot_closest_to_centre.pt,
                                                                 maximum_pixels_between_contours=9)

if args.display_images:
    number_recognition.draw_image_with_contours(img, central_contours)

number_recognition._mask_with_contours(img, central_contours)

if args.display_images:
    cv2.imshow("Masked image", img)
    cv2.waitKey(0)

# Try to recognise the number
recognised_number = number_recognition.recognise_rotated_number(img)

print("Recognised number: {!r}".format(recognised_number.numeric_value))
print("Probable spot location: {!r}".format(recognised_number.dot_location_yx))
