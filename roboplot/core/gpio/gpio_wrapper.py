"""
Wraps the GPIO library, so defining a single place to switch between the real GPIO library, and the emulator + gui.

By default the emulator will be used. To use the RPi.GPIO module, export the environment variable ROBOPLOT=1 in the
console before running (this should eventually be setup in the .bashrc of the pi).
If for some reason you wish to do this through pycharm, it may be helpful to note that you can set extra environment
variables available:
 - to a script by editing its 'Run Configurations'
 - in the console by going to 'File -> Settings -> Build, Execution, Deployment -> Console -> Python Console'
"""

import os

is_emulator = os.environ.get('ROBOPLOT', 0) == 0

if is_emulator:
    from roboplot.core.gpio.EmulatorGUI import GPIO, app
else:
    import RPi.GPIO as GPIO  # For use on the pi

GPIO.setmode(GPIO.BCM)


# TODO: Look into using the atexit modue instead of calling directly in scripts? I'm not sure whether this will execute on exceptions though...
def clean_up():
    GPIO.cleanup()

    if is_emulator:
        print('\nExiting Emulator GUI... (focus on another window to complete the exit)')
        app.root.quit()  # Still needs tweaking -- something stops the gui from quitting when it has focus...
