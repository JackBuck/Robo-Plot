"""
Contains various configuration variables for the roboplot module.

Attributes:
    roboplot_directory (str): A convenient reference to the installed location of the roboplot package on disk.
"""

import os

# File Paths
roboplot_directory = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
resources_dir = os.path.normpath(os.path.join(roboplot_directory, '..', 'resources'))