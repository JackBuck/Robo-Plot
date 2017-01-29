#!/usr/bin/env python3

import argparse
import time

import numpy as np

import context
import roboplot.core.curves as curves
import roboplot.core.gpio.gpio_wrapper as gpio_wrapper
import roboplot.core.hardware as hardware

try:
    wait = 0
    pen_millimetres_per_second = 1000
    centre = [10, 10]
    radius = 5

    for i in range(0, 10):
        # Draw a circle
        circle = curves.Circle(centre, radius)

        # Move to start of path.
        line_to_start = curves.LineSegment(hardware.both_axes.current_location, circle.get_start_point())
        hardware.both_axes.follow(curve=line_to_start, pen_speed=pen_millimetres_per_second)

        start_time = time.time()
        hardware.both_axes.follow(curve=circle, pen_speed=pen_millimetres_per_second)
        end_time = time.time()

        x = 10 + 2*(i+1)*(i+1)
        y = centre[0] + 15
        centre = [y, x]
        radius += x/2

    # Report statistics
    print('Elapsed: ', end='')
    print(end_time - start_time)
    print('Predicted: ', end='')
    print(2 * np.pi * radius / pen_millimetres_per_second)

finally:
    gpio_wrapper.clean_up()
