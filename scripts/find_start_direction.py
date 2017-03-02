import context
import cv2
import argparse
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.path_following as path_following
import roboplot.core.config as config

config.init_()

# Commandline arguments
parser = argparse.ArgumentParser(description='Find start direction from given image')
parser.add_argument('-f', '--file_path', type=str, required=True,
                    help='the file path of the image to be analysed')

args = parser.parse_args()
inFile = args.file_path

image = cv2.imread(inFile, cv2.IMREAD_GRAYSCALE)

start_direction = path_following.determine_starting_direction(image)

print(start_direction)
cv2.waitKey(0)
print("Done")
