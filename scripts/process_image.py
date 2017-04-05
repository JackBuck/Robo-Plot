#!/usr/bin/env python3

import argparse
import os

import cv2
import numpy as np
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Displays the preprocessing applied to an image containing a number in '
                                             'preparation for number recognition')
parser.add_argument('filepath', type=str, help='the path to an image to clean')

img = cv2.imread('/home/jack/Pictures/Current6/Hackspace_RoboPlot/NumberRecognition/20pt_0deg.jpg',
                 cv2.IMREAD_GRAYSCALE)
if img is None:
    raise TypeError("Could not load image!")

img_blur = cv2.medianBlur(img, ksize=5)
img_thresh = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
img_blur_thresh = cv2.adaptiveThreshold(img_blur, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)

## Show the images
images = [img, img_blur, img_thresh, img_blur_thresh]
titles = ['original', 'blurred', 'Adaptive Gaussian Thresholding', 'Adaptive Gaussian Thresholding (after blur)']

for i in range(4):
    plt.subplot(2, 2, i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.xticks([]), plt.yticks([])
plt.show()

# cv2.imshow('image', img)
# cv2.waitKey(0)
