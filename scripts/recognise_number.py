#! /usr/bin/env python3

import argparse
import PIL.Image as Image

import cv2
import pytesseract


def read_image(file_path):
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        return img
    else:
        raise TypeError("Could not open image file!")


def clean_image(img):
    img = cv2.medianBlur(img, ksize=5)
    img = cv2.adaptiveThreshold(img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
    return img


def recognise_number(img):
    img = Image.fromarray(img)

    # psm 8 => single word;
    # digits => use the digits config file supplied with the software
    recognised_text = pytesseract.image_to_string(img, config='-psm 8 digits')
    return recognised_text


if __name__ == '__main__':
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Recognise a supplied number.')
    parser.add_argument('input_file', type=str, help='the path to the file containing the number to recognise.')
    args = parser.parse_args()

    # Script body
    img = read_image(args.input_file)
    img = clean_image(img)
    recognised_text = recognise_number(img)
    print(recognised_text)
