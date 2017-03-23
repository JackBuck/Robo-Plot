#! /usr/bin/env python3

import argparse

import context
import roboplot.dottodot.number_recognition as number_recognition


if __name__ == '__main__':
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Recognise a supplied number.')
    parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
    parser.add_argument('-d', '--display-images', action='store_true', help='display intermediate results.')
    args = parser.parse_args()

    # Load and Process the image
    img = number_recognition.DotToDotImage.load_image_from_file(args.input_file)
    recognised_number = img.process_image()

    print("Recognised number: {!r}".format(recognised_number.numeric_value))
    print("Probable spot location: {!r}".format(recognised_number.dot_location_yx))

    # Save and display images
    img.save_intermediate_images()

    if args.display_images:
        img.display_intermediate_images()
