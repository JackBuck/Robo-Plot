#!/usr/bin/env python3

import argparse

import cv2

import context
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.colour_detection as cd

# Commandline arguments
parser = argparse.ArgumentParser(description='Take a photo and find the green in')

parser.add_argument('-c', '--centre', metavar=('y', 'x'), nargs=2, type=float, default=[260, 180],
                    help='the centre (y,x) of the photo to be taken (note only relevant in debug o/w photo taken in '
                         'current camera position)')
parser.add_argument('-m', '--minsize', type=float, default=10,
                    help='the minimum size of green to be detected')
parser.add_argument('-d', '--display-images', action='store_true', help='display results.')
args = parser.parse_args()

a_camera = camera_wrapper.Camera()
photo = a_camera.take_photo_at(args.centre)

hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
(cX, cY) = cd.detect_green(hsv_image, args.minsize, change_to_white=False)

if cX != -1:
    print("Done: Green Found")
    if args.display_images:
        cv2.circle(photo, (cX, cY), radius=5, color=(255, 10, 10), thickness=2)
        cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)

else:
    print("Done: Green Not Found")
    if args.display_images:
        cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)
