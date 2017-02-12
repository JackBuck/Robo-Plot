import context
import cv2
import argparse
import roboplot.core.Camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.colour_detection as cd
import numpy as np


# Commandline arguments
parser = argparse.ArgumentParser(description='Take a photo and find the red in')

parser.add_argument('-c', '--centre', metavar=('x', 'y'), nargs=2, type=float, default=[180, 30],
                        help='the centre (x,y) of the photo to be taken (note only relevant in debug o/w'
                             'photo taken in current camera position)')
parser.add_argument('-m', '--minsize', type=float, default=10,
                    help='the minimum size of red to be detected')

args = parser.parse_args()

a_camera = camera_wrapper.Camera()
photo = a_camera.take_photo_at(args.centre)

hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
(cX, cY) = cd.detect_red(hsv_image, args.minsize, False)

if cX != -1:
    cv2.circle(photo, (cX, cY), 5, (255, 10, 10), 2)
    cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
    cv2.waitKey(0)
    print("Done: Red Found")

else:
    cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
    cv2.waitKey(0)
    print("Done: Red Not Found")
