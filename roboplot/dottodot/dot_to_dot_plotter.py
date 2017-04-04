import collections
import os
import statistics
import warnings

import cv2
import numpy as np

import roboplot.config as config
import roboplot.dottodot.clustering as clustering
import roboplot.dottodot.curve_creation as curve_creation
import roboplot.dottodot.number_recognition as number_recognition
import roboplot.dottodot.job_processing_station as job_processing_station
import roboplot.imgproc.page_search as page_search
from roboplot.core.plotter import Plotter


class DotToDotPlotter:
    _min_millimetres_between_distinct_spots = 2.5
    temporary_directory = config.number_recognition_tmp_dir

    def __init__(self, plotter: Plotter, save_and_reload_all_photos: bool = False):
        """
        Create an object capable of solving a dot-to-dot.

        Args:
            plotter (Plotter): a plotter, providing an interface to the hardware
            save_and_reload_all_photos: if true then all photos taken will be initially saved as .jpg files and reloaded
        """
        self._plotter = plotter
        self.save_and_reload_all_photos = save_and_reload_all_photos
        self._number_clusters = []  # type: list[GlobalNumberCluster]

        self._file_name_provider = FileNameProvider(filename_pattern='tmp_{}.jpg')
        self._processing_station = None

    def do_dot_to_dot(self) -> None:
        """Take pictures to explore the page for dots, then draw a picture to join them."""
        if not self._plotter.is_homed:
            self._plotter.home()

        numbers = self.search_for_numbers()
        self.draw_joined_dots(numbers)

    def search_for_numbers(self, max_numeric_value_allowed=99):
        """
        Take photos of the page to determine all the numbers and their locations.

        Args:
            max_numeric_value_allowed (int): if the plotter recognises a number greater than this, it will try to
                                             retake that number.

        Returns:
            list[number_recognition.GlobalNumber]: the recognised numbers
        """

        self._processing_station = job_processing_station.JobProcessingStation(name='Image processing station')

        target_positions = _compute_raster_scan_positions(self._plotter.camera_field_of_view_xy_mm)
        recognised_numbers = self._take_and_analyse_initial_photos(target_positions)
        self._number_clusters = self._group_nearby_numbers(recognised_numbers)

        self._retake_photos_until_unique_valid_candidate_at_each_location(max_numeric_value_allowed)
        self._remove_unrecognised_number_clusters()  # Unnecessary?
        self._retake_photos_to_remove_repeated_numeric_values()
        self._retake_last_number_if_last_two_are_not_consecutive()  # Unfortunately if this leads us to discover
        # another incorrect number, we will not retake that one...

        self._processing_station.signal_no_more_jobs()

        candidates = [c for c in [grp.best_guess for grp in self._number_clusters] if c.numeric_value is not None]
        candidates = sorted(candidates, key=lambda n: n.numeric_value)
        _warn_if_unexpected_numeric_values(candidates)

        return candidates

    def _take_and_analyse_initial_photos(self, target_positions):
        processing_jobs = []
        for target_position in target_positions:
            processing_jobs.append(self._take_photo_and_extract_numbers(target_position))

        self._processing_station.join()

        recognised_numbers = []
        for job in processing_jobs:
            new_global_numbers = job.return_value
            recognised_numbers.extend(new_global_numbers)

        return recognised_numbers

    def _group_nearby_numbers(self, recognised_numbers):
        groups = clustering.group_objects(recognised_numbers,
                                          distance_function=_millimetres_between_numbers,
                                          min_dist_between_items_in_different_groups=self._min_millimetres_between_distinct_spots)
        return [GlobalNumberCluster(grp) for grp in groups]

    def _retake_photos_until_unique_valid_candidate_at_each_location(self, max_numeric_value_allowed) -> None:
        """
        Process the current set of recognised numbers to extract a list with a single element for each unique
        location in the recognised numbers.

        This method may induce the plotter to take more photos if it needs more information.

        Args:
            max_numeric_value_allowed (int): if the plotter recognises a number greater than this, it will try to
                                             retake that number.
        """
        for grp in self._number_clusters:
            assert len(grp) > 0, 'Groups returned from the clustering should all be non-empty!!'
            self._retake_photos_until_valid_mode(grp,
                                                 mode_is_invalid=lambda m: m is None or m > max_numeric_value_allowed)

    def _retake_photos_to_remove_repeated_numeric_values(self) -> None:
        # Find repeated elements
        # noinspection PyArgumentList
        numeric_value_counts = collections.Counter([c.modal_numeric_value for c in self._number_clusters])
        clusters_with_repeated_numeric_value = []  # type: list[GlobalNumberCluster]
        for cluster in self._number_clusters:
            numeric_value = cluster.modal_numeric_value
            if numeric_value is not None and numeric_value_counts[numeric_value] > 1:
                clusters_with_repeated_numeric_value.append(cluster)

        if len(clusters_with_repeated_numeric_value) > 0:
            print('Repeated numeric values- {}'.format(
                ', '.join(['{}: {}'.format(n, numeric_value_counts[n])
                           for n in numeric_value_counts if numeric_value_counts[n] > 1])))

        # Retake photos
        for current_cluster in clusters_with_repeated_numeric_value:
            old_numeric_value = current_cluster.modal_numeric_value

            self._retake_photos_until_valid_mode(current_cluster,
                                                 mode_is_invalid=lambda m: m is None or numeric_value_counts[m] > 1)

            new_numeric_value = current_cluster.modal_numeric_value
            numeric_value_counts[old_numeric_value] -= 1
            numeric_value_counts[new_numeric_value] += 1

            for cluster in self._number_clusters:
                if cluster.modal_numeric_value == new_numeric_value and \
                                cluster not in clusters_with_repeated_numeric_value:
                    clusters_with_repeated_numeric_value.append(cluster)  # In python these extra items do get iterated!

    def _retake_last_number_if_last_two_are_not_consecutive(self) -> None:
        last_two_numbers_might_not_be_consecutive = True

        while last_two_numbers_might_not_be_consecutive:
            last_two_numbers_might_not_be_consecutive = False

            clusters = [grp for grp in self._number_clusters if grp.modal_numeric_value is not None]
            sorted_clusters = sorted(clusters, key=lambda c: c.modal_numeric_value)  # type: list[GlobalNumberCluster]

            if len(sorted_clusters) > 1:
                largest_numeric_value = sorted_clusters[-1].modal_numeric_value
                second_largest_numeric_value = sorted_clusters[-2].modal_numeric_value
                if largest_numeric_value != second_largest_numeric_value + 1:
                    self._retake_photos_until_valid_mode(
                        sorted_clusters[-1], mode_is_invalid=lambda m: m is None or m == largest_numeric_value)
                    if sorted_clusters[-1].modal_numeric_value < largest_numeric_value:  # If it got smaller...
                        last_two_numbers_might_not_be_consecutive = True

    def _retake_photos_until_valid_mode(self, target_number_cluster, mode_is_invalid=lambda m: m is None) -> None:
        """
        Take 0 or more extra photos at the average location of the target numbers to do what we can to ensure a
        valid modal numeric value exists.

        Args:
            target_number_cluster (GlobalNumberCluster):
                The different representations of a single real life number to be recognised. This is extended to
                include all extra photos taken during this method.

            mode_is_invalid:
                A function which accepts a given mode (int) and returns true if it is invalid. By default this simply
                returns True if a unique mode does not exist.
        """
        average_location = target_number_cluster.average_dot_location_yx
        numeric_value = target_number_cluster.modal_numeric_value

        jitters = np.array([[0, 0],
                            [10, 0],
                            [0, 10],
                            [-10, 0],
                            [0, -10]])

        retry_number = -1
        while mode_is_invalid(numeric_value) and retry_number + 1 < len(jitters):
            retry_number += 1

            # Take a new photo
            print('Could not determine number at location ({0[0]:.0f},{0[1]:.0f}), current value {1}\n'
                  'Retrying...'.format(average_location, numeric_value))
            processing_job = self._take_photo_and_extract_numbers(average_location + jitters[retry_number])
            self._processing_station.join()
            new_global_numbers = processing_job.return_value

            new_global_numbers = [n for n in new_global_numbers
                                  if np.linalg.norm(
                    n.dot_location_yx_mm - average_location) < self._min_millimetres_between_distinct_spots]
            number_recognition.print_recognised_global_numbers(new_global_numbers)

            target_number_cluster.extend(new_global_numbers)

            # Try again to get the mode values
            numeric_value = _try_compute_mode([n.numeric_value for n in target_number_cluster])

    def _take_photo_and_extract_numbers(self, target_position: (float, float)):
        self._plotter.move_camera_to(target_position)
        photo = self._plotter.take_greyscale_photo_at(target_position, padding_gray_value=255)

        class ProcessImageJob(job_processing_station.Job):
            def __init__(self, dot_to_dot_plotter: DotToDotPlotter, photo: np.ndarray):
                super().__init__()
                self._d2dplotter = dot_to_dot_plotter
                self._photo = photo

            def _do_work_core(self):
                if self._d2dplotter.save_and_reload_all_photos:
                    self._photo = self._d2dplotter._save_and_reload_photo(self._photo)

                dot_to_dot_image = number_recognition.DotToDotImage(self._photo)
                dot_to_dot_image.process_image()

                new_global_numbers = [number_recognition.GlobalNumber.from_local(n, target_position)
                                      for n in dot_to_dot_image.recognised_numbers]

                self.return_value = new_global_numbers
                self.print_output = number_recognition.print_recognised_global_numbers_to_string(new_global_numbers)

        job = ProcessImageJob(self, photo)
        self._processing_station.add_job(job)

        return job

    def _save_and_reload_photo(self, photo: np.ndarray) -> np.ndarray:
        if not os.path.isdir(self.temporary_directory):
            os.mkdir(self.temporary_directory, 0o750)  # drwxr-x---

        file_path = os.path.join(self.temporary_directory, self._file_name_provider.get_next_name())

        cv2.imwrite(file_path, photo)
        while True:
            # Just in case (we don't have time to test if this loop is actually necessary!!)
            photo = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if photo is not None:
                break
            warnings.warn('Could not immediately reload image:\n{}'.format(file_path))

        try:
            os.remove(file_path)
        except OSError:
            warnings.warn('Could not delete file:\n{}'.format(file_path))
            # The file is probably in use on a windows pc
            # The user can clean them up themselves later (or this program will happily overwrite them next time round)
            pass

        return photo

    def _remove_unrecognised_number_clusters(self):
        self._number_clusters = [n for n in self._number_clusters if n.modal_numeric_value is not None]

    def draw_joined_dots(self, dot_to_dot_numbers) -> None:
        """
        Draw a picture, joining the dots between the numbers.

        Args:
            dot_to_dot_numbers (list[number_recognition.GlobalNumber]):
        """
        path_curve = curve_creation.points_to_svg_line_segments([n.dot_location_yx_mm for n in dot_to_dot_numbers],
                                                                is_closed=True)
        self._plotter.draw(path_curve)


class GlobalNumberCluster(list):
    def __init__(self, initial_global_numbers=()):
        """
        Args:
            initial_global_numbers (list[number_recognition.GlobalNumber]):
        """
        # noinspection PyTypeChecker
        list.__init__(self, initial_global_numbers)

    @property
    def best_guess(self):
        return number_recognition.GlobalNumber(
            self.modal_numeric_value,
            self.average_dot_location_yx)

    @property
    def modal_numeric_value(self):
        return _try_compute_mode([n.numeric_value for n in self])

    @property
    def average_dot_location_yx(self):
        return _average_dot_location(self)


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
        if final_numbers[i].numeric_value != i + 1:
            warnings.warn('Did not find a set of consecutive numbers starting at 1!\n'
                          'Instead found {}'.format(', '.join([str(n.numeric_value) for n in final_numbers])))
            break


class FileNameProvider:
    """A simple, class to provide unique file names."""

    def __init__(self, filename_pattern: str = 'tmp_{}'):
        """
        Args:
            filename_pattern (str): str.format(index) will be called on the pattern to return the next filename. Here
                                    index refers to an internally maintained counter to ensure all returned filenames
                                    are unique.
        """
        self.index = 0
        self.pattern = filename_pattern

    def get_next_name(self) -> str:
        """Return the next file name in the sequence."""
        file_name = self.pattern.format(self.index)
        self.index += 1
        return file_name
