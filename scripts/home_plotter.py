#!/usr/bin/env python3

import threading
import time

import context
import roboplot.core.hardware as hardware

axes = hardware.both_axes


def report_position():
    while True:
        print("\rCurrent Location = ({0[0]: 7.2f}, {0[1]: 7.2f})".format(axes.current_location), end='')
        time.sleep(0.1)


try:
    threading.Thread(target=report_position, daemon=True).start()
    axes.home()
    time.sleep(0.2)

finally:
    hardware.cleanup()
