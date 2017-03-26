#!/usr/bin/env python3

import argparse
import statistics
import time
import warnings

import numpy as np
import svgpathtools as svg

import context
import roboplot.core.hardware as hardware
import roboplot.imgproc.page_search as page_search
import roboplot.dottodot.clustering as clustering
import roboplot.dottodot.number_recognition as number_recognition
import roboplot.svg.svg_parsing as svg_parsing
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
            [number_recognition.GlobalNumber.from_local(n, target_position) for n in dot_to_dot_image.recognised_numbers])

    end_time = time.time()
    print('Time to collect photos: {:.1f} seconds'.format(end_time-start_time))

    # Filter the results
    def millimetres_between_numbers(first: number_recognition.GlobalNumber, second: number_recognition.GlobalNumber):
        return np.linalg.norm(first.dot_location_yx_mm - second.dot_location_yx_mm)

    groups = clustering.group_objects(recognised_numbers,
                                      distance_function=millimetres_between_numbers,
                                      min_dist_between_items_in_different_groups=5)

    final_numbers = []
    for group in groups:
        assert len(group) > 0, 'Groups returned from the clustering should all be non-empty!!'

        location_yx_mm = np.mean([number.dot_location_yx_mm for number in group], axis=0)

        # Try to get the modal numeric value
        try:
            numeric_value = statistics.mode([n.numeric_value for n in group])
        except statistics.StatisticsError:
            numeric_value = None

        num_retries = 0
        while numeric_value is None and num_retries < 3:
            num_retries += 1

            # Take a new photo
            print('Could not determine number at location ({0[0]:.0f},{0[1]:.0f}).\nRetrying...'.format(location_yx_mm))
            plotter.move_camera_to(location_yx_mm)
            photo = camera.take_photo_at(location_yx_mm)

            dot_to_dot_image = number_recognition.DotToDotImage(photo)
            dot_to_dot_image.process_image()
            dot_to_dot_image.print_recognised_numbers()

            global_numbers = [number_recognition.GlobalNumber(n, location_yx_mm) for n in dot_to_dot_image.recognised_numbers]
            group.extend([n for n in global_numbers if np.linalg.norm(n.dot_location_yx_mm - location_yx_mm) < 5])

            # Try again to get the mode values
            try:
                numeric_value = statistics.mode([n.numeric_value for n in group])  # This _is_ 'None' friendly
            except statistics.StatisticsError:  # No unique value, or empty data
                numeric_value = None

        if numeric_value is not None:
            final_numbers.append(number_recognition.GlobalNumber(numeric_value, location_yx_mm))

    final_numbers = sorted(final_numbers, key=lambda n: n.numeric_value)

    # Warn if we don't have a list of unique, consecutive numbers starting at 1
    for i in range(len(final_numbers)):
        if final_numbers[i].numeric_value != i:
            warnings.warn('Did not find a set of consecutive numbers starting at 1!\n'
                          'Instead found {}'.format(', '.join([n.numeric_value for n in final_numbers])))
            break

    # Draw the dot-to-dot
    path = svg.Path()
    for i in range(1, len(final_numbers)):
        path.append(svg.Line(svg_parsing.yx_to_complex(final_numbers[i-1].dot_location_yx_mm),
                             svg_parsing.yx_to_complex(final_numbers[i].dot_location_yx_mm)))

    if len(final_numbers) > 0:
        path.append(svg.Line(svg_parsing.yx_to_complex(final_numbers[-1].dot_location_yx_mm),
                             svg_parsing.yx_to_complex(final_numbers[0].dot_location_yx_mm)))

    path_curve = svg_parsing.SVGPath(path, mm_per_unit=1)

    plotter.draw(path_curve)

finally:
    GPIO.cleanup()
