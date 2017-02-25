import context
import cv2
import argparse
import numpy as np

from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.colour_detection as cd
import roboplot.challenge_two_functions as challenge2


try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Move around the paper and find green')
    
    parser.add_argument('-m', '--minsize', type=float, default=10,
                        help='the minimum size of green to be detected')
    
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    
    args = parser.parse_args()



    centre = challenge2.find_green_triangle(args.pen_millimetres_per_second, args.minsize)
    
    centre = challenge2.find_green_centre(centre, args.pen_millimetres_per_second, args.minsize)
finally:
    GPIO.cleanup()

print("Done")


