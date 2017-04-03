#!/usr/bin/env python3

import threading
import time

import context
import roboplot.core.hardware as hardware
from roboplot.core.gpio.gpio_wrapper import GPIO


class Reporter(threading.Thread):
    end_thread = False

    def __init__(self, axes):
        super().__init__(target=self.report_position, name='Reporter', daemon=True)
        self._axes = axes

    def report_position(self):
        while not self.end_thread:
            print("\rCurrent Location = ({0[0]: 7.2f}, {0[1]: 7.2f})".format(self._axes.current_location), end='')
            time.sleep(0.1)

try:
    axes = hardware.both_axes

    reporter = Reporter(axes)
    reporter.start()

    start_time = time.time()

    axes.home()

    end_time = time.time()
    time.sleep(0.2)

    reporter.end_thread = True
    print('\nElapsed: {:.2f} seconds'.format(end_time-start_time))

finally:
    reporter.end_thread = True
    GPIO.cleanup()
