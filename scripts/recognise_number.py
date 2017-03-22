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

    # Display images
    if args.display_images:
        number_recognition.draw_image_with_keypoints(img.clean_image, [img.centre_spot], "Clean with centre spot")
        number_recognition.draw_image_with_contours(img.clean_image, img.central_contours, "Clean with centre contours")
        number_recognition.draw_image(img.masked_image, "Masked image")
