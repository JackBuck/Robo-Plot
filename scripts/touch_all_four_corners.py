#!/usr/bin/env python3

import context
import roboplot.core.hardware as hardware

hardware.plotter.home()

a4 = [297, 210]
hardware.plotter.move_to([a4[0], 0])
hardware.plotter.move_to([0, 0])
hardware.plotter.move_to([0, a4[1]])
hardware.plotter.move_to(a4)
