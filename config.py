"""
This module houses global variables which need to be shared across files.

All global variables are declared here.

"""

def init_():
    global use_dummy_photo
    global debug
    use_dummy_photo = False
    debug = False



def init_position():
    global position
    position = (0, 0)