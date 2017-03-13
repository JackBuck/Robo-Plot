import context
import cv2
import argparse
import numpy as np

from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.challenge_two_functions as challenge2

try:
    centre = challenge2.find_green_triangle(32, 20)
    centre, photo = challenge2.find_green_centre(centre, 32, 20)

    # Need function to compute first direction here.

    computed_camera_path = path_following.compute_complete_path(image, starting_direction)
    path_following.follow_computed_path(computed_camera_path)


finally:
    GPIO.cleanup()

print("Done")


