#!/usr/bin/env python3

import argparse
import time
import glob
import pickle

import context
import roboplot.core.hardware as hardware
import roboplot.dottodot.curve_creation as curve_creation
import roboplot.dottodot.data_capture as data_capture
from roboplot.core.camera.dummy_camera_from_image_paths import DummyCameraFromImagePaths
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

    # camera = hardware.camera
    image_paths = sorted(glob.glob('/home/jack/Documents/SoftwareDevelopment/Projects/Hackspace2016-2017/Resources'
                                   '/OutputFromDotToDot_Bat_3/Photo*.jpg'))
    camera = DummyCameraFromImagePaths(resolution_pixels_xy=(200, 200), pixels_to_mm_scale_factors_xy=(0.233, 0.237),
                                       image_paths=image_paths)

    # Scan the bed for photos
    plotter.home()

    # Take and analyse the photos
    start_time = time.time()
    final_numbers = data_capture.search_for_numbers(camera, plotter)
    end_time = time.time()
    print('Time to collect and analyse photos: {:.1f} seconds'.format(end_time - start_time))

    # Draw the dot-to-dot
    # tmpsavefile = '/tmp/roboplot_final_numbers'
    # with open(tmpsavefile, 'wb') as f:
    #     pickle.dump(final_numbers, f)

    # with open(tmpsavefile, 'rb') as f:
    #     final_numbers = pickle.load(f)

    # path_curve = curve_creation.points_to_line_segments([n.dot_location_yx_mm for n in final_numbers], is_closed = True)
    path_curve = curve_creation.points_to_svg_line_segments([n.dot_location_yx_mm for n in final_numbers],
                                                            is_closed=True)
    plotter.draw(path_curve)

finally:
    GPIO.cleanup()
