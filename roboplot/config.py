"""
Contains various configuration variables for the roboplot module.

Attributes:
    roboplot_directory (str): A convenient reference to the installed location of the roboplot package on disk.
"""

import os

# File Paths
roboplot_directory = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
resources_dir = os.path.normpath(os.path.join(roboplot_directory, '..', 'resources'))
test_data_dir = os.path.join(resources_dir, 'test_data')

# Environment variables
real_hardware = os.environ.get('ROBOPLOT', '0') != '0'
if real_hardware:
    print("Using real hardware")
else:
    print("Using simulated hardware")

# Debugging image paths
debug_image_file_path = os.path.join(resources_dir, 'Challenge_2_Test_Images', 'HackspacePath_Sample4.png')
debug_output_folder = os.path.join(resources_dir, 'DebugImages')


# Camera constants
X_PIXELS_TO_MILLIMETRE_SCALE = 1
Y_PIXELS_TO_MILLIMETRE_SCALE = 1


CAMERA_RESOLUTION = (200, 200)

camera_offset = (0.0, 2.0)  # Needs calibration. This is translation to move from pen centre to camera centre.
