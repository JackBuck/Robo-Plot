#!/usr/bin/env python3

"""
Executing this script will run all tests in this folder in a file starting with test_*
To run tests from a single file only execute that single file.
Test data required for tests should be kept in the resources/test_data/test_name
For more information see unittest documentation.
"""

import glob
import unittest

# noinspection PyUnresolvedReferences
from test_runner import CustomTestRunner

test_files = glob.glob('test_*.py')
module_strings = [test_file[0:len(test_file) - 3] for test_file in test_files]
suites = [unittest.defaultTestLoader.loadTestsFromName(test_file) for test_file in module_strings]
test_suite = unittest.TestSuite(suites)
test_runner = CustomTestRunner()
result = test_runner.run(test_suite)
