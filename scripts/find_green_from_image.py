import argparse

import cv2

import context
import roboplot.imgproc.colour_detection as cd


# Commandline arguments
parser = argparse.ArgumentParser(description='Find green in a given image')
parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be analysed')
parser.add_argument('-m', '--minsize', type=float, required=True,
                    help='the minimum size of green to be detected')

args = parser.parse_args()

# Script body
inFile = args.file_path
print(inFile)
image = cv2.imread(inFile)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
(cX, cY) = cd.detect_green(hsv_image, args.minsize, False)
cv2.circle(image, (cX, cY), 5, (255, 10, 10), 3)
cv2.imshow('Centre', cv2.resize(image, (500, 500)))
cv2.waitKey(0)
print("Done")
