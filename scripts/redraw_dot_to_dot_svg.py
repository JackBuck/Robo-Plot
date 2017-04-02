#!/usr/bin/env python3

import argparse

import svgpathtools as svg

import context
import roboplot.dottodot.curve_creation as curve_creation

# Commandline arguments
parser = argparse.ArgumentParser(description='Redraw a single Bezier curve in an svg file, using the protocol for '
                                             'autosmoothing nodes.')
parser.add_argument('input_file', type=str, help='the path to the svg file containing the single bezier curve to '
                                                 'redraw.')
parser.add_argument('output_file', type=str, help='the location at which to save the redrawn svg.')
args = parser.parse_args()

# Load the file
paths, attributes, svg_attributes = svg.svg2paths2(args.input_file)

# Save the file
svg.disvg(paths, filename=args.output_file)
