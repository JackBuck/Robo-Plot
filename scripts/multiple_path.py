import time

import context
import roboplot.core.hardware as hardware
import roboplot.imgproc.colour_detection as colour_detection
import roboplot.imgproc.start_end_detection as start_end_detection
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.page_search as page_search
import roboplot.imgproc.path_following as path_following
from roboplot.core.gpio.gpio_wrapper import GPIO

start_time = time.time()

try:
    # Home axes.

    hardware.plotter.home()

    # Calculate the list of positions photos need to be taken at to walk round the outside of the paper.
    camera_positions = page_search.compute_positions(210, 297, 40)


    # Walk round to each position and analyse the photo taken at that position.
    for i in range(0, len(camera_positions)):

        camera_centre = camera_positions[i]
        green_location, photo = start_end_detection.find_green_at_position(camera_centre, 10)

        # Check if any green was detected.
        if green_location[0] != -1:
            green_found = True

            centre, photo = start_end_detection.find_green_centre(green_location, 20)

            a_path_finder = path_following.PathFinder()
            a_path_finder.compute_complete_path(photo, centre)
            a_path_finder.follow_computed_path()

    end_time = time.time()

finally:
    GPIO.cleanup()

print("Done")
