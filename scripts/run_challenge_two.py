import context
import cv2
import argparse
import numpy as np

from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.challenge_two_functions as challenge2
import roboplot.core.hardware as hardware


try:
    # Home axes.
    hardware.both_axes.home()

    centre = challenge2.find_green_triangle(32, 20)
    centre, photo = challenge2.find_green_centre(centre, 32, 20)

    # Need function to compute first direction here.

    gray_scale_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
    starting_direction = image_analysis.find_start_direction(gray_scale_photo)

    computed_camera_path = path_following.compute_complete_path(gray_scale_photo, starting_direction)
    path_following.follow_computed_path(computed_camera_path)


finally:
    GPIO.cleanup()

print("Done")


