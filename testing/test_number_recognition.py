#!/usr/bin/env python3

"""A suite of regression tests for the number recognition."""

import glob
import os
import re
import unittest

import context
import roboplot.config as config
from roboplot.dottodot.number_recognition import DotToDotImage


class NumberRecognitionRegressionTests(unittest.TestCase):
    test_data_directory = os.path.join(config.test_data_dir, 'number_recognition')

    def test_on_selection_of_sizes(self):
        """Regression test number recognition on potentially rotated images."""
        file_glob = os.path.join(self.test_data_directory, '*.jpg')
        for img_file in glob.glob(file_glob):
            filename = os.path.basename(img_file)
            file_name_match = re.match(
                r'(?P<numeric_value>\d+)_(?P<fontsize>\d+)pt_(?P<angle>\d+)deg_y(?P<spot_y>\d+)_x(?P<spot_x>\d+)',
                filename)
            with self.subTest(filename = filename):
                # Perform the number recognition
                img = DotToDotImage.load_image_from_file(img_file)
                number = img.process_image()

                # Extract expected results
                expected_number = int(file_name_match.group('numeric_value'))
                expected_spot_location = (int(file_name_match.group('spot_y')),
                                          int(file_name_match.group('spot_x')))

                # Compare
                self.assertEqual(number.numeric_value, expected_number)
                self.assertAlmostEqual(number.dot_location_yx[0], expected_spot_location[0], delta=2)
                self.assertAlmostEqual(number.dot_location_yx[1], expected_spot_location[1], delta=2)


if __name__ == '__main__':
    unittest.main()
