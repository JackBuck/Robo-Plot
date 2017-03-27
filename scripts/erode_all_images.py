import argparse
import os

import cv2

import roboplot.imgproc.image_analysis as image_analysis

# Commandline arguments
parser = argparse.ArgumentParser(description='Process all images in folder')
parser.add_argument('filepath', type=str,
                        help='a (relative or absolute) path to folder of images to be processed')

args = parser.parse_args()

file_list = [f for f in os.listdir(args.filepath) if
             os.path.isfile(os.path.join(args.filepath, f))]
for file_name in file_list:
    image = cv2.imread(args.filepath + "/" + file_name)
    if image is not None:
        image = image_analysis.process_image(image)
        cv2.imwrite(args.filepath + "/" + file_name, image)
