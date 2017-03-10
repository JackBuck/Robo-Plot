import argparse
import os

import cv2

import context
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.config as config

parser = argparse.ArgumentParser(description='Take a photo at the current position.')
parser.add_argument('savepath', type=str, nargs='?', default=os.path.join(config.debug_output_folder, 'Photo.jpg'),
                    help='the location at which to save the image')
args = parser.parse_args()

# I haven't implemented the simulated camera because I don't need it and it would take time to work out how it works
assert config.real_hardware, "This script does not currently support the simulated camera."

camera = camera_wrapper.Camera()
photo = camera.take_photo_at(None)
cv2.imwrite(args.savepath, photo)
