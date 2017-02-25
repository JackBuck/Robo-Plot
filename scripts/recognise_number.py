#! /usr/bin/env python3

import argparse
import PIL.Image as Image

import cv2
import pytesseract

# Commandline arguments
parser = argparse.ArgumentParser(description='Recognise a supplied number.')
parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
args = parser.parse_args()

# Script body
img = cv2.imread(args.input_file, cv2.IMREAD_GRAYSCALE)
if img is None:
    raise TypeError("Could not open image file!")

img = cv2.medianBlur(img, ksize=5)
img = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
img = Image.fromarray(img)

# psm 8 => single word;
# digits => use the digits config file supplied with the software
recognised_text = pytesseract.image_to_string(img,config='-psm 8 digits')

print(recognised_text)
