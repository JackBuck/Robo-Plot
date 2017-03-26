#!/usr/bin/env python3

import argparse
import time

import context
import roboplot.core.hardware as hardware
import roboplot.imgproc.page_search as page_search
import roboplot.dottodot.number_recognition as number_recognition
from roboplot.core.gpio.gpio_wrapper import GPIO


try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Do all or part of the dot-to-dot challenge')
    args = parser.parse_args()

    # Get hardware
    # TODO: It would be nicer to encapsulate this so that we don't need to know what camera the plotter is using
    # Hannah has put a take_photo() method on the plotter, so we just need to also funnel the page_search method into the
    # plotter as well somehow.
    plotter = hardware.plotter
    camera = hardware.camera

    # Scan the bed for photos
    a4_height_y_mm = 297
    a4_width_x_mm = 210
    target_positions = page_search.compute_positions(a4_width_x_mm, a4_height_y_mm,
                                                     photo_size=int(camera.resolution_mm[0]),
                                                     millimetres_between_photos=int(camera.resolution_mm[0]/2))

    plotter.home()

    # Take and analyse the photos
    start_time = time.time()

    recognised_numbers = []
    for target_position in target_positions:
        plotter.move_camera_to(target_position)
        photo = camera.take_photo_at(target_position)

        dot_to_dot_image = number_recognition.DotToDotImage(photo)
        dot_to_dot_image.process_image()
        dot_to_dot_image.print_recognised_numbers()

        recognised_numbers.extend(
            [number_recognition.GlobalNumber.from_local(n) for n in dot_to_dot_image.recognised_numbers])

    end_time = time.time()
    print('Time to collect photos: {:.1f} seconds'.format(end_time-start_time))

finally:
    GPIO.cleanup()
