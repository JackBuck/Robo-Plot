import context
import sys
import cv2
import os

import roboplot.imgproc.colour_detection as cd
import roboplot.core.config as config

config.init_()
global debug
debug = True

# Arg version.

#os.getcwd()
#inFile = os.getcwd() + "\\" + sys.argv[1]
#print(inFile)
#hsv_image = cv2.imread(inFile, cv2.COLORMAP_HSV)
#(cX, cY) = cd.detect_green(hsv_image, sys.argv[2], False)
#
#print("Done")


#Hardcoded version
inFile = "C:/Users/Hannah/Documents/Hackspace/Robo-Plot_Clone/resources/Challenge_2_Test_Images/greentriangle.jpg"

hsv_image = cv2.imread(inFile)

cv2.imshow("Image", hsv_image)

hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2HSV)
(cX, cY) = cd.detect_green(hsv_image, 10, False)

x=0
