import unittest

import context
from roboplot.core.gpio import gpio_wrapper as gpio_wrapper


class CustomTestRunner(unittest.TextTestRunner):
    """ A test runner which behaves the same as the TextTestRunner, but which closes the emulator gui when all tests
    have been run."""
    def run(self, test):
        result = super().run(test)
        try:
            gpio_wrapper.clean_up()
        finally:
            return result
