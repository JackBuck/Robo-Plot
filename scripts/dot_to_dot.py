#!/usr/bin/env python3

import argparse
import time
import glob
import pickle

import context
import roboplot.core.hardware as hardware
import roboplot.dottodot.curve_creation as curve_creation
from roboplot.dottodot.dot_to_dot_plotter import DotToDotPlotter
from roboplot.core.camera.dummy_camera_from_image_paths import DummyCameraFromImagePaths
from roboplot.core.gpio.gpio_wrapper import GPIO


try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Do all or part of the dot-to-dot challenge')
    parser.add_argument('-g', '--file-glob', type=str, default=None,
                        help='If specified, then the camera will be simulated using ascii sorted image files matching '
                             'this file glob')
    args = parser.parse_args()

    # Get hardware
    if args.file_glob is not None:
        image_paths = sorted(glob.glob(args.file_glob))
        hardware.plotter._camera = camera = DummyCameraFromImagePaths(resolution_pixels_xy=(200, 200),
                                                                      pixels_to_mm_scale_factors_xy=(0.233, 0.237),
                                                                      image_paths=image_paths)
    plotter = DotToDotPlotter(hardware.plotter)


    # Do the dot-to-dot
    start_time = time.time()
    plotter.do_dot_to_dot()
    end_time = time.time()
    print('Elapsed: {:.0f} seconds'.format(end_time - start_time))

finally:
    GPIO.cleanup()
