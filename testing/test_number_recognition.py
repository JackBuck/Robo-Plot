#!/usr/bin/env python3

"""A suite of regression tests for the number recognition."""

import glob
import os
import re
import unittest

import numpy as np

import context
import roboplot.config as config
import roboplot.dottodot.number_recognition as number_recognition


class NumberRecognitionRegressionTests(unittest.TestCase):
    test_data_directory = os.path.join(config.test_data_dir, 'number_recognition')

    def test_on_selection_of_sizes(self):
        """Regression test number recognition on potentially rotated images."""
        file_glob = os.path.join(self.test_data_directory, 'various_sizes', '*.jpg')
        for img_file in glob.glob(file_glob):
            filename = os.path.basename(img_file)
            file_name_match = re.match(
                r'(?P<numeric_value>\d+)_(?P<fontsize>\d+)pt_(?P<angle>\d+)deg_y(?P<spot_y>\d+)_x(?P<spot_x>\d+)',
                filename)

            expected_number = number_recognition.Number(numeric_value=int(file_name_match.group('numeric_value')),
                                                        dot_location_yx=(int(file_name_match.group('spot_y')),
                                                                         int(file_name_match.group('spot_x'))))
            self._test_on_file(img_file, [expected_number])

    def test_on_bat_images(self):
        """Regression test number recognition on images for the bat dot-to-dot"""
        file_glob = os.path.join(self.test_data_directory, 'bat_size_20', '*.jpg')
        for img_file in glob.glob(file_glob):
            filename = os.path.basename(img_file)

            expected_numbers = []
            for file_name_match in re.finditer(r'(?P<numeric_value>\d+)_y(?P<spot_y>\d+)_x(?P<spot_x>\d+)', filename):
                numeric_value = int(file_name_match.group('numeric_value'))
                dot_location_yx = (int(file_name_match.group('spot_y')), int(file_name_match.group('spot_x')))
                expected_numbers.append(number_recognition.Number(numeric_value, dot_location_yx))

            self._test_on_file(img_file, expected_numbers)

    def _test_on_file(self, file_path, expected_numbers):
        with self.subTest(filename=os.path.basename(file_path)):
            # Perform the number recognition
            img = number_recognition.DotToDotImage.load_image_from_file(file_path)
            recognised_numbers = img.process_image()

            # Compare
            for expected_number in expected_numbers:
                recognised_numbers_at_this_location =\
                    [n for n in recognised_numbers if np.allclose(n.dot_location_yx, expected_number.dot_location_yx,
                                                                  rtol=0, atol=2)]

                self.assertEqual(len(recognised_numbers_at_this_location), 1,
                                 'More than one number found at the same location.')

                recognised_number = recognised_numbers_at_this_location[0]

                self.assertEqual(recognised_number.numeric_value, expected_number.numeric_value)


if __name__ == '__main__':
    unittest.main()
