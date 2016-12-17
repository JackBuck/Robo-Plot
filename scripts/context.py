"""
Provides a reference to the 'roboplot' module, for use by scripts in the 'scripts' directory.

When a script attempts to import the 'roboplot' module, the interpreter first searches for a built-in module
with that name. If not found, it then searches in the locations specified in sys.path.
The variable sys.path is initialised from
 - the directory containing the input script (i.e. the scripts directory),
 - the PYTHONPATH environment variable (if exported),
 - the installation-dependent default.
Since the roboplot directory is, by default, in none of these, the script will not be able to find it.

This module provides a solution to that problem. Scripts in the 'scripts' directory should include the line
``from context import roboplot`` before importing any modules from roboplot.

References: https://docs.python.org/3.4/tutorial/modules.html#the-module-search-path
"""

import sys
import os


_script_dir = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
_roboplot_parentdir = os.path.normpath(os.path.join(_script_dir, '..'))
sys.path.insert(0, _roboplot_parentdir)

import roboplot

if __name__ == '__main__':
    print("This file is not intended to be run as a script!", end="\n\n")
    print("Help on module context:")
    print(__doc__)
