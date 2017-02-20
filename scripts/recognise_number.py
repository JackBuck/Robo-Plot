#! /usr/bin/env python3

import argparse
import PIL.Image as Image

import pytesseract


# Commandline arguments
parser = argparse.ArgumentParser(description='Recognise a supplied number.')
parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
args = parser.parse_args()

# Script body
recognised_text = pytesseract.image_to_string(
    Image.open(args.input_file),
    config='-psm 8 digits')  # psm 8 => single word; digits => use the digits config file supplied with the software

print(recognised_text)
