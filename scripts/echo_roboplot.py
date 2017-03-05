#!/usr/bin/env python3

import os


ROBOPLOT = os.environ.get('ROBOPLOT', '0')
print("ROBOPLOT='{}'".format(ROBOPLOT), end="  --  ")
if ROBOPLOT != '0':
    print("Using real hardware")
else:
    print("Using simulated hardware")
