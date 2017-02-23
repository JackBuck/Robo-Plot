#!/usr/bin/env python3

import unittest


class HardwareRepositoryTest(unittest.TestCase):
    @staticmethod
    def test_can_import_hardware_module():
        # noinspection PyUnresolvedReferences
        import roboplot.core.hardware


if __name__ == '__main__':
    unittest.main()
