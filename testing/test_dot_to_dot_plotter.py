#!/usr/bin/env python3

import unittest
import unittest.mock as mock

import numpy as np

import context
from roboplot.core.plotter import Plotter
from roboplot.dottodot.dot_to_dot_plotter import DotToDotPlotter
from roboplot.dottodot.number_recognition import GlobalNumber


# TODO: Refactor this to remove the copying and pasting surrounding creating the side_effects


class TestDotToDotPlotter(unittest.TestCase):
    def setUp(self):
        self._mock_plotter = mock.MagicMock(name='plotter',
                                            spec_set=Plotter,
                                            camera_field_of_view_xy_mm=(200, 200))

        self._dot_to_dot_plotter = DotToDotPlotter(self._mock_plotter)

    def test_retakes_images_until_mode_found(self):
        # Arrange
        self._dot_to_dot_plotter._take_and_analyse_initial_photos = mock.MagicMock(
            return_value=[GlobalNumber(1, (20, 20)),
                          GlobalNumber(None, (20, 40))])

        take_photo_and_extract_numbers_mock = mock.MagicMock(
            side_effect=[[GlobalNumber(None, (20, 40))],
                         [GlobalNumber(2, (20, 40))],
                         [GlobalNumber(2, (20, 40))],
                         [GlobalNumber(2, (20, 40))]])

        self._dot_to_dot_plotter._take_photo_and_extract_numbers = take_photo_and_extract_numbers_mock

        # Act
        candidates = self._dot_to_dot_plotter.search_for_numbers()

        # Assert
        self.assertEqual(take_photo_and_extract_numbers_mock.call_count, 4)
        for args, kwargs in take_photo_and_extract_numbers_mock.call_args_list:
            self.assertEqual(len(args), 1)
            np.testing.assert_allclose(args[0], (20, 40), rtol=0, atol=20)

    def test_retakes_images_of_repeated_numbers(self):
        # Arrange
        self._dot_to_dot_plotter._take_and_analyse_initial_photos = mock.MagicMock(
            return_value=[GlobalNumber(1, (20, 20)),
                          GlobalNumber(1, (20, 80))])

        def side_effect(*args, **kwargs):
            if np.linalg.norm(args[0] - np.array([20, 20])) < 20:
                return [GlobalNumber(1, [20, 20])]
            elif np.linalg.norm(args[0] - np.array([20, 80])) < 20:
                return [GlobalNumber(2, [20, 80])]
            else:
                return []

        take_photo_and_extract_numbers_mock = mock.MagicMock(side_effect=side_effect)
        self._dot_to_dot_plotter._take_photo_and_extract_numbers = take_photo_and_extract_numbers_mock

        # Act
        candidates = self._dot_to_dot_plotter.search_for_numbers()

        # Assert
        num_times_number_2_rephotographed = \
            len([args for args, kwargs in take_photo_and_extract_numbers_mock.call_args_list
                 if all(abs(args[0] - np.array([20, 80])) < 20)])

        self.assertEqual(num_times_number_2_rephotographed, 2)

        self.assertCountEqual(
            [(c.numeric_value, c.dot_location_yx_mm[0], c.dot_location_yx_mm[1]) for c in candidates],
            [(1, 20, 20), (2, 20, 80)])

    def test_retakes_images_of_repeated_numbers_which_are_only_discovered_when_retaking_other_numbers(self):
        # Arrange
        self._dot_to_dot_plotter._take_and_analyse_initial_photos = mock.MagicMock(
            return_value=[GlobalNumber(1, (20, 20)),
                          GlobalNumber(1, (20, 80)),
                          GlobalNumber(2, (60, 20))])

        def side_effect(*args, **kwargs):
            if np.linalg.norm(args[0] - np.array([20, 20])) < 20:
                return [GlobalNumber(1, [20, 20])]
            elif np.linalg.norm(args[0] - np.array([20, 80])) < 20:
                return [GlobalNumber(2, [20, 80])]
            elif np.linalg.norm(args[0] - np.array([60, 20])) < 20:
                return [GlobalNumber(3, [60, 20])]
            else:
                return []

        take_photo_and_extract_numbers_mock = mock.MagicMock(side_effect=side_effect)
        self._dot_to_dot_plotter._take_photo_and_extract_numbers = take_photo_and_extract_numbers_mock

        # Act
        candidates = self._dot_to_dot_plotter.search_for_numbers()

        # Assert
        num_times_number_3_rephotographed = \
            len([args for args, kwargs in take_photo_and_extract_numbers_mock.call_args_list
                 if np.linalg.norm(args[0] - np.array([60, 20])) < 20])

        self.assertEqual(num_times_number_3_rephotographed, 2)

        self.assertCountEqual(
            [(c.numeric_value, c.dot_location_yx_mm[0], c.dot_location_yx_mm[1]) for c in candidates],
            [(1, 20, 20), (2, 20, 80), (3, 60, 20)])

    def test_does_not_retake_images_of_numbers_which_are_not_repeated(self):
        # Arrange
        self._dot_to_dot_plotter._take_and_analyse_initial_photos = mock.MagicMock(
            return_value=[GlobalNumber(1, (20, 20)),
                          GlobalNumber(None, (20, 80)),
                          GlobalNumber(2, (20, 80))])

        take_photo_and_extract_numbers_mock = mock.MagicMock(return_value=[GlobalNumber(2, [20, 80])])
        self._dot_to_dot_plotter._take_photo_and_extract_numbers = take_photo_and_extract_numbers_mock

        # Act
        candidates = self._dot_to_dot_plotter.search_for_numbers()

        # Assert
        for args, kwargs in take_photo_and_extract_numbers_mock.call_args_list:
            assert not all(abs(args[0] - np.array([20, 20])) < 20)

        self.assertCountEqual(
            [(c.numeric_value, c.dot_location_yx_mm[0], c.dot_location_yx_mm[1]) for c in candidates],
            [(1, 20, 20), (2, 20, 80)])

    def test_by_default_retakes_three_digit_numbers(self):
        # Arrange
        self._dot_to_dot_plotter._take_and_analyse_initial_photos = mock.MagicMock(
            return_value=[GlobalNumber(111, (20, 20))])

        take_photo_and_extract_numbers_mock = mock.MagicMock(return_value=[GlobalNumber(11, [20, 20])])
        self._dot_to_dot_plotter._take_photo_and_extract_numbers = take_photo_and_extract_numbers_mock

        # Act
        candidates = self._dot_to_dot_plotter.search_for_numbers()

        # Assert
        self.assertEqual(take_photo_and_extract_numbers_mock.call_count, 2)
        self.assertCountEqual(
            [(c.numeric_value, c.dot_location_yx_mm[0], c.dot_location_yx_mm[1]) for c in candidates],
            [(11, 20, 20)])
