import statistics
import warnings

import cv2
import numpy as np

import roboplot.dottodot.clustering as clustering
import roboplot.dottodot.curve_creation as curve_creation
import roboplot.dottodot.number_recognition as number_recognition
import roboplot.imgproc.page_search as page_search
from roboplot.core.plotter import Plotter


class DotToDotPlotter:
    def __init__(self, plotter: Plotter):
        self._plotter = plotter

    def do_dot_to_dot(self) -> None:
        """Take pictures to explore the page for dots, then draw a picture to join them."""
        if not self._plotter.is_homed:
            self._plotter.home()

        numbers = self.search_for_numbers()
        self.draw_joined_dots(numbers)

    def search_for_numbers(self):
        """
        Take photos of the page to determine all the numbers and their locations.

        Returns:
            list[number_recognition.GlobalNumber]: the recognised numbers
        """

        # TODO: Sort out this illegal reference to a _camera
        target_positions = _compute_raster_scan_positions(self._plotter._camera.resolution_mm_xy)
        recognised_numbers = self._take_and_analyse_initial_photos(target_positions)
        final_numbers = self._extract_sorted_numbers_at_unique_locations(recognised_numbers)

        _warn_if_unexpected_numeric_values(final_numbers)

        return final_numbers

    def _take_and_analyse_initial_photos(self, target_positions):
        recognised_numbers = []
        for target_position in target_positions:
            new_global_numbers = self._take_photo_and_extract_numbers(target_position)
            recognised_numbers.extend(new_global_numbers)

        return recognised_numbers

    def _extract_sorted_numbers_at_unique_locations(self, recognised_numbers):
        """
        Process the current set of recognised numbers to extract a list with a single element for each unique
        location in the recognised numbers. The list is sorted by numeric value.

        This method may induce the plotter to take more photos if it needs more information.

        Args:
            recognised_numbers (list[number_recognition.GlobalNumber]): the collection of all numbers recognised so far

        Returns:
            list[number_recognition.GlobalNumber]: a list of numbers, one for each recognised location, sorted by
                                                   numeric value
        """
        groups = clustering.group_objects(recognised_numbers,
                                          distance_function=_millimetres_between_numbers,
                                          min_dist_between_items_in_different_groups=5)
        final_numbers = []
        for group in groups:
            assert len(group) > 0, 'Groups returned from the clustering should all be non-empty!!'
            numeric_value, group = self._retake_photos_until_unique_mode(group)

            if numeric_value is not None:
                final_numbers.append(number_recognition.GlobalNumber(numeric_value, _average_dot_location(group)))

        return sorted(final_numbers, key=lambda n: n.numeric_value)

    def _retake_photos_until_unique_mode(self, target_numbers):
        """
        Take 0 or more extra photos at the average location of the target numbers in order to find the modal numeric
        value recognised.

        Args:
            target_numbers (list[number_recognition.GlobalNumber]): the different representations of a single real
                                                                    life number to be recognised

        Returns:
            (int, list[number_recognition.GlobalNumber]): the first return value is the modal numeric value
                                                          the second return value is the augmented list of global numbers
        """
        target_numbers = target_numbers.copy()

        average_location = _average_dot_location(target_numbers)

        numeric_value = _try_compute_mode([n.numeric_value for n in target_numbers])

        jitters = np.array([[0, 0],
                            [10, 0],
                            [10, 10],
                            [0, 10]])

        retry_number = -1
        while numeric_value is None and retry_number + 1 < len(jitters):
            retry_number += 1

            # Take a new photo
            print('Could not determine number at location ({0[0]:.0f},{0[1]:.0f}).\n'
                  'Retrying...'.format(average_location))
            new_global_numbers = self._take_photo_and_extract_numbers(average_location + jitters[retry_number])
            new_global_numbers = [n for n in new_global_numbers
                                  if np.linalg.norm(n.dot_location_yx_mm - average_location) < 5]

            number_recognition.print_recognised_global_numbers(new_global_numbers)
            target_numbers.extend(new_global_numbers)

            # Try again to get the mode values
            numeric_value = _try_compute_mode([n.numeric_value for n in target_numbers])

        return numeric_value, target_numbers

    def _take_photo_and_extract_numbers(self, target_position: (float, float)):
        self._plotter.move_camera_to(target_position)
        photo = self._plotter.take_greyscale_photo_at(target_position, padding_gray_value=255)

        dot_to_dot_image = number_recognition.DotToDotImage(photo)
        dot_to_dot_image.process_image()

        new_global_numbers = [number_recognition.GlobalNumber.from_local(n, target_position)
                              for n in dot_to_dot_image.recognised_numbers]
        number_recognition.print_recognised_global_numbers(new_global_numbers)

        return new_global_numbers

    def draw_joined_dots(self, dot_to_dot_numbers) -> None:
        """
        Draw a picture, joining the dots between the numbers.

        Args:
            dot_to_dot_numbers (list[number_recognition.GlobalNumber]):
        """
        path_curve = curve_creation.points_to_svg_line_segments([n.dot_location_yx_mm for n in dot_to_dot_numbers],
                                                                is_closed=True)
        self._plotter.draw(path_curve)


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


def _millimetres_between_numbers(first: number_recognition.GlobalNumber,
                                 second: number_recognition.GlobalNumber) -> float:
    return np.linalg.norm(first.dot_location_yx_mm - second.dot_location_yx_mm)


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
