"""
Wraps the Camera library, so defining a single place to switch between the real Camera library, and the emulator.

By default the emulator will be used. To use the PiCamera module, export the environment variable ROBOPLOT=1 in the
console before running (this should eventually be setup in the .bashrc of the pi).
If for some reason you wish to do this through pycharm, it may be helpful to note that you can set extra environment
variables available:
 - to a script by editing its 'Run Configurations'
 - in the console by going to 'File -> Settings -> Build, Execution, Deployment -> Console -> Python Console'
"""

import os


is_emulator = os.environ.get('ROBOPLOT', 0) == 0

if is_emulator:
    from roboplot.core.Camera.dummy_camera import DummyCamera as Camera
else:
    # from roboplot.core.Camera.pi_camera import Camera
    from roboplot.core.Camera.remote_camera import RemoteCamera as Camera


