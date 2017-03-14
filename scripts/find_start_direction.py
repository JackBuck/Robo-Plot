#!/usr/bin/env python3

import argparse

import cv2

import context
import roboplot.imgproc.image_analysis as image_analysis


# Commandline arguments
parser = argparse.ArgumentParser(description='Find start direction from given image')
parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be analysed')

args = parser.parse_args()
inFile = args.file_path

image = cv2.imread(inFile, cv2.IMREAD_GRAYSCALE)

start_direction = image_analysis.find_start_direction(image)

print('Done, start direction is: ' + str(start_direction))

