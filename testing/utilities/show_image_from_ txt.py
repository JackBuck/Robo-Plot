#!/usr/bin/env python3

import argparse

import numpy as np
import cv2

# Commandline arguments
parser = argparse.ArgumentParser(description='Display image saved as txt file')

parser.add_argument('filepath', type=str,
                    help='a (relative or absolute) path to the text file')
                
args = parser.parse_args()

numpytxt = np.loadtxt(args.filepath)

cv2.imshow('Image from text', numpytxt)
cv2.waitKey(0)
