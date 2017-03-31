import context
import time

import cv2
import argparse
import numpy as np

import roboplot.config as config
from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.imgproc.path_following as path_following
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.page_search as page_search
import roboplot.challenge_two_functions as challenge2
import roboplot.core.hardware as hardware

start_time = time.time()

try:
    # Home axes.

    hardware.plotter.home()

    # Calculate the list of positions photos need to be taken at to walk round the outside of the paper.
    camera_positions = page_search.compute_positions(210, 297, 40)


    # Walk round to each position and analyse the photo taken at that position.
    for i in range(0, len(camera_positions)):

        camera_centre = camera_positions[i]
        green_location, photo = challenge2.find_green_at_position(camera_centre, 10)

        # Check if any green was detected.
        if green_location[0] != -1:
            green_found = True

            centre, photo = challenge2.find_green_centre(green_location, 20)

            # Need function to compute first direction here.
            starting_direction = image_analysis.find_start_direction(photo)
            computed_camera_path = path_following.compute_complete_path(photo, centre, starting_direction)
            path_following.follow_computed_path(computed_camera_path)

    end_time = time.time()

finally:
    GPIO.cleanup()

print("Done")
