#!/usr/bin/env python3

import argparse
import time
import cv2

import numpy as np

import context
import roboplot.imgproc.pre_processing as pre_processing
from matplotlib import pyplot as plt

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Erode an image')
    parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be eroded')


    args = parser.parse_args()
    img = cv2.imread(args.file_path)

    # Erode image
    
    a_pre_processor = pre_processing.PreProcessing()
    img = a_pre_processor.global_threshold(img)
    eroded_image = a_pre_processor.erosion(img)
    
    images = [img, eroded_image]
          
    titles = ['Original Image','Eroded Image']
    
    plt.figure()
    plt.subplot(1,2,1)
    plt.imshow(img, 'gray')
    plt.subplot(1,2,2)
    plt.imshow(eroded_image,'gray')
    plt.show()

    cv2.waitKey(0)

finally:
    pass
   




