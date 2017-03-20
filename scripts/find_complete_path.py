import context
import cv2
import argparse
import numpy as np

import roboplot.config as config
from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.challenge_two_functions as challenge2
import roboplot.core.hardware as hardware


try:
    # Home axes.
   # hardware.both_axes.home()

    global_centre = challenge2.find_green_triangle(32, 20)
    centre, photo = challenge2.find_green_centre(global_centre, 32, 20)

    # Need function to compute first direction here.

    starting_direction = image_analysis.find_start_direction(photo)

    computed_camera_path = path_following.compute_complete_path(photo, starting_direction)


finally:
    GPIO.cleanup()

print("Done")

