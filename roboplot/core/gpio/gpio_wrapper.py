"""
Wraps the GPIO library, so defining a single place to switch between the real GPIO library, and the emulator + gui.
"""


is_emulator = True  # Change this to False on the raspberry pi

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
