import statistics
import warnings

import cv2
import numpy as np

import roboplot.dottodot.clustering as clustering
import roboplot.dottodot.number_recognition as number_recognition
import roboplot.imgproc.page_search as page_search
from roboplot.core.plotter import Plotter
from roboplot.core.camera.camera_wrapper import Camera


def search_for_numbers(camera: Camera, plotter: Plotter):
    """
    Take photos of the page to determine all the numbers and their locations.

    Args:
        plotter (Plotter): the plotter to use
        camera (Camera): the camera to use (in the future this will be removed all access piped through the plotter)

    Returns:
        list[number_recognition.GlobalNumber]: the recognised numbers
    """
    target_positions = _compute_raster_scan_positions(camera.resolution_mm_xy)

    if not plotter.is_homed:
        plotter.home()

    recognised_numbers = _take_and_analyse_initial_photos(camera, plotter, target_positions)
    final_numbers = _extract_sorted_numbers_at_unique_locations(camera, plotter, recognised_numbers)
    _warn_if_unexpected_numeric_values(final_numbers)

    return final_numbers


def _compute_raster_scan_positions(camera_resolution_mm_xy: (float, float),
                                   page_dimensions_mm_xy: (float, float) = page_search.a4_paper_width_height):
    """
    Computes a set of target locations for taking photos in order to cover the whole page.

    Every number is guaranteed to appear not-near-the-edge of *some* photo.

    Args:
        camera_resolution_mm_xy (float, float):
        page_dimensions_mm_xy (float, float):

    Returns:
        list[list[int]]: the target positions for taking photos
    """

    return page_search.compute_positions(int(page_dimensions_mm_xy[0]), int(page_dimensions_mm_xy[1]),
                                         photo_size=int(camera_resolution_mm_xy[0]),
                                         millimetres_between_photos=int(camera_resolution_mm_xy[0] / 2))


def _take_and_analyse_initial_photos(camera: Camera, plotter: Plotter, target_positions):
    recognised_numbers = []
    for target_position in target_positions:
        new_global_numbers = _take_photo_and_extract_numbers(camera, plotter, target_position)
        recognised_numbers.extend(new_global_numbers)

    return recognised_numbers


def _take_photo_and_extract_numbers(camera: Camera, plotter: Plotter, target_position: (float, float)):
    plotter.move_camera_to(target_position)
    photo = camera.take_photo_at(target_position)
    photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)

    dot_to_dot_image = number_recognition.DotToDotImage(photo)
    dot_to_dot_image.process_image()

    new_global_numbers = [number_recognition.GlobalNumber.from_local(n, target_position)
                          for n in dot_to_dot_image.recognised_numbers]
    number_recognition.print_recognised_global_numbers(new_global_numbers)

    return new_global_numbers


def _millimetres_between_numbers(first: number_recognition.GlobalNumber,
                                 second: number_recognition.GlobalNumber) -> float:
    return np.linalg.norm(first.dot_location_yx_mm - second.dot_location_yx_mm)


def _extract_sorted_numbers_at_unique_locations(camera: Camera, plotter: Plotter, recognised_numbers):
    """
    Args:
        camera:
        plotter:
        recognised_numbers (list[number_recognition.GlobalNumber]):

    Returns:
        list[number_recognition.GlobalNumber]
    """
    groups = clustering.group_objects(recognised_numbers,
                                      distance_function=_millimetres_between_numbers,
                                      min_dist_between_items_in_different_groups=5)
    final_numbers = []
    for group in groups:
        assert len(group) > 0, 'Groups returned from the clustering should all be non-empty!!'
        numeric_value, group = _retake_photos_until_unique_mode(camera, plotter, group)

        if numeric_value is not None:
            final_numbers.append(number_recognition.GlobalNumber(numeric_value, _average_dot_location(group)))

    return sorted(final_numbers, key=lambda n: n.numeric_value)


def _retake_photos_until_unique_mode(camera: Camera, plotter: Plotter, target_numbers, maximum_retries: int = 3):
    """
    Take 0 or more extra photos at the average location of the target numbers in order to find the modal numeric
    value recognised.

    Args:
        camera (Camera):
        plotter (Plotter):
        target_numbers (list[number_recognition.GlobalNumber]): the different representations of a single real
                                                                life number to be recognised

    Returns:
        (int, list[number_recognition.GlobalNumber]): the first return value is the modal numeric value
                                                      the second return value is the augmented list of global numbers
    """
    target_numbers = target_numbers.copy()

    average_location = _average_dot_location(target_numbers)

    numeric_value = _try_compute_mode([n.numeric_value for n in target_numbers])

    num_retries = 0
    while numeric_value is None and num_retries < maximum_retries:
        num_retries += 1

        # Take a new photo
        print('Could not determine number at location ({0[0]:.0f},{0[1]:.0f}).\nRetrying...'.format(average_location))
        new_global_numbers = _take_photo_and_extract_numbers(camera, plotter, average_location)
        new_global_numbers = [n for n in new_global_numbers
                              if np.linalg.norm(n.dot_location_yx_mm - average_location) < 5]

        number_recognition.print_recognised_global_numbers(new_global_numbers)
        target_numbers.extend(new_global_numbers)

        # Try again to get the mode values
        numeric_value = _try_compute_mode([n.numeric_value for n in target_numbers])

    return numeric_value, target_numbers


def _try_compute_mode(objects):
    """
    Computes the mode of a set of object, if a unique such exists.

    Args:
        objects (list[T]): the object whose mode is to be computed

    Returns:
        T: the modal value, or None if a unique mode does not exist
    """
    try:
        numeric_value = statistics.mode(objects)  # This _is_ 'None' friendly
    except statistics.StatisticsError:  # No unique value, or empty data
        numeric_value = None
    return numeric_value


def _average_dot_location(group_of_numbers):
    return np.mean([number.dot_location_yx_mm for number in group_of_numbers], axis=0)


def _warn_if_unexpected_numeric_values(final_numbers) -> None:
    """
    Warn if the supplied numeric values are not consecutive starting at 1.

    Args:
        final_numbers (list[number_recognition.GlobalNumber]): the final set of recognised numbers
    """
    for i in range(len(final_numbers)):
        if final_numbers[i].numeric_value != i:
            warnings.warn('Did not find a set of consecutive numbers starting at 1!\n'
                          'Instead found {}'.format(', '.join([str(n.numeric_value) for n in final_numbers])))
            break
