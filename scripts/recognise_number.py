#! /usr/bin/env python3

import argparse

import context
import roboplot.dottodot.number_recognition as number_recognition


if __name__ == '__main__':
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Recognise a supplied number.')
    parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
    parser.add_argument('-r', '--possibly-rotated', action='store_true',
                        help='set this flag to indicate that the number could be rotated')
    args = parser.parse_args()

    # Load the image
    img = number_recognition.read_image(args.input_file)

    # Extract the numeric value
    if args.possibly_rotated:
        try:
            recognised_number = number_recognition.recognise_rotated_number(img)
        except ValueError:
            recognised_number = "No spot!!"
    else:
        recognised_number = number_recognition.recognise_number(img)

    print("Recognised number: {!r}".format(recognised_number.numeric_value))
    print("Probable spot location: {!r}".format(recognised_number.dot_location_yx))
