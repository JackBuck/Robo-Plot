#!/usr/bin/env python3

import time

import context
import roboplot.core.hardware as hardware
import roboplot.imgproc.start_end_detection as start_end_detection
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.path_following as path_following
from roboplot.core.gpio.gpio_wrapper import GPIO

start_time = time.time()

try:
    # Home axes.

    start_time = time.time()

    hardware.plotter.home()
    global_centre = start_end_detection.find_green_triangle(min_size=50)
    centre, photo = start_end_detection.find_green_centre(global_centre, 20)

    # Find path
    a_path_finder = path_following.PathFinder()
    a_path_finder.compute_complete_path(photo, centre)

    # Follow Path
    a_path_finder.follow_computed_path()

    end_time = time.time()
    print('Elapsed: {} seconds'.format(end_time - start_time))

    # Present paper.

    hardware.plotter.move_pen_to([148.5, 0])

finally:
    GPIO.cleanup()

print("Done")


