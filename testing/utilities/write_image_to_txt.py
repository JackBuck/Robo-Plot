#!/usr/bin/env python3

import argparse
import numpy as np
import cv2

# Commandline arguments
parser = argparse.ArgumentParser(description='Show numpy array written as text file as image')

parser.add_argument('filepath', type=str,
                help='a (relative or absolute) path to the text file')
                
args = parser.parse_args()

image = cv2.imread(args.filepath)

cv2.imshow('Image from text', image)
cv2.waitKey(0)

with open ('imageastxt.txt', 'wb') as f:
    reshaped_image = image.reshape((image.shape[0], image.shape[1]*3))
    np.savetxt(f, reshaped_image, fmt='%d')