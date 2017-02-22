"""
Adds the location of the 'roboplot' module to sys.path for use by scripts in the 'scripts' directory.

When a script attempts to import the 'roboplot' module, the interpreter searches for
 - a module already imported with that name,
 - a built-in module or a frozen module with that name,
 - a module in one of the locations specified in sys.path.

The variable sys.path is initialised from
 - the directory containing the input script (i.e. the scripts directory),
 - the PYTHONPATH environment variable (if exported),
 - the installation-dependent default.
Since the roboplot directory is, by default, in none of these, the script will not be able to find it.

This module provides a solution to that problem. Scripts in the 'scripts' directory should include the line
``import context`` before importing any modules from roboplot.

References: https://docs.python.org/3.4/tutorial/modules.html#the-module-search-path
            https://docs.python.org/3.4/reference/import.html#searching
"""

import sys
import os

_script_dir = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
_roboplot_parentdir = os.path.normpath(os.path.join(_script_dir, '..'))
sys.path.insert(0, _roboplot_parentdir)

if __name__ == '__main__':
    print("This file is not intended to be run as a script!", end="\n\n")
    print("Help on module context:")
    print(__doc__)
