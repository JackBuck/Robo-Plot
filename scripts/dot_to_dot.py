#!/usr/bin/env python3

import argparse
import time
import glob
import os
import shutil

import context
import roboplot.config as config
import roboplot.core.hardware as hardware
from roboplot.dottodot.dot_to_dot_plotter import DotToDotPlotter
from roboplot.core.camera.dummy_camera_from_image_paths import DummyCameraFromImagePaths
from roboplot.core.gpio.gpio_wrapper import GPIO


def find_free_debug_images_subfolder() -> str:
    desired_name = 'DotToDot_$1'
    new_folder = None
    i = 0
    while new_folder is None or os.path.exists(new_folder):
        new_folder = os.path.join(config.debug_output_folder, desired_name.replace('$1', str(i)))
        i += 1

    return new_folder

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

    debug_images_copy_target = find_free_debug_images_subfolder()
    os.mkdir(debug_images_copy_target)
    for f in glob.glob(os.path.join(config.debug_output_folder, '*.jpg')):
        shutil.copy2(f, debug_images_copy_target)

finally:
    GPIO.cleanup()
