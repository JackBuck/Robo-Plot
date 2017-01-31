import context
import cv2
import argparse
import roboplot.imgproc.colour_detection as cd
import roboplot.core.config as config

config.init_()

# Commandline arguments
parser = argparse.ArgumentParser(description='Find green in a given image')
parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be analysed')
parser.add_argument('-m', '--minsize', type=float, required=True,
                    help='the minimum size of green to be detected')

args = parser.parse_args()
inFile = args.file_path
print(inFile)
image = cv2.imread(inFile)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
(cX, cY) = cd.detect_green(hsv_image, args.minsize, False)
cv2.circle(image, (cX, cY), 20, (255, 10, 10), 10)
cv2.imshow('Centre', cv2.resize(image, (500, 500)))
cv2.waitKey(0)
print("Done")
