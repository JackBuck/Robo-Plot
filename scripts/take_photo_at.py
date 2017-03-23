#!/usr/bin/env python3

import argparse
import time

import cv2 as cv2

import context
import roboplot.config as config
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO
from roboplot.core.camera.camera_wrapper import Camera

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Moves to given location and takes photo')
    parser.add_argument('-c', '--centre', metavar=('y', 'x'), nargs=2, type=float, default=[150, 100],
                        help='the centre (y,x) of the photo wanted')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')
    parser.add_argument('-w', '--wait', type=float, default=0,
                        help='an initial sleep time in seconds (default: %(default)s)')
    parser.add_argument('-f', '--file_path', type=str, required=False, default=None,
                        help='where the image will be saved')
    args = parser.parse_args()
    time.sleep(args.wait)
    
    # Needs homing 
    hardware.plotter.home()
    hardware.plotter.move_camera_to(args.centre)
    image = hardware.plotter.take_photo()

    if args.file_path is not None:
        cv2.imwrite(args.file_path, image)

finally:
    GPIO.cleanup()
