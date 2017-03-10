import argparse

import numpy as np
import cv2

import context
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.config as config


# Commandline arguments
parser = argparse.ArgumentParser(description='Find line moving south from centre '
                                             'of the top of the image')
parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be analysed')


args = parser.parse_args()
inFile = args.file_path

image = cv2.imread(inFile)
image = np.array(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
image = cv2.resize(image, (200, 100))
pixel_points = image_analysis.compute_pixel_path(image, image.shape[1]/2)
cv2.waitKey(0)
print("Done")
