"""
This module wraps either wiringpi or the GPIO emulator gui.

It also performs initial setup of the wiringpi module.

*Note:* I have only filled in the members we are currently using. If you want to call something else, feel free - you
just need to add it to this wrapper!
"""

import warnings

import roboplot.config as _config

if _config.real_hardware:
    import wiringpi

else:
    import roboplot.core.gpio.fake_wiringpi as wiringpi

# Global setup
wiringpi.wiringPiSetupGpio()  # Use BCM pin numbering

pwm_pin = None  # We are only supporting one pwm pin


def setup_pwm_pin_18(initial_value: float = 0):
    """
    Sets up pin 18 PWM.

    This method is required because the order of the calls to the methods required to setup a pwm pin through
    wiringpi matters and is mystical!

    Be warned -- This method will only allow you to setup pin 18 in a hardcoded way! You can however read the
    configuration variables used by looking at the pwm_pin attribute of this module.

    Args:
        initial_value (float): a value to set after setting up the pin for pwm
    """
    global pwm_pin
    if pwm_pin is not None:
        warnings.warn('Cannot set up pwm pin more than once! Skipping setup...')
        return

    pwm_pin = PWMPinInfo(pin_number=18, pwm_range=500, pwm_clock_divisor=765)
    wiringpi.pinMode(pwm_pin.pin_number, wiringpi.PWM_OUTPUT)  # Set SERVO pin as PWM output
    wiringpi.pwmWrite(pwm_pin.pin_number, 0)  # Turn output off

    # TODO: Ask Luke to explain these three pwm setup functions...
    wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)  # Set PWM mode as mark space (as opposed to balanced - the default)
    wiringpi.pwmSetRange(pwm_pin.pwm_range)  # Set PWM range (range of duty cycles)
    wiringpi.pwmSetClock(pwm_pin.pwm_clock_divisor)  # Set PWM clock divisor
    # Note: PWM Frequency = 19.2MHz / (pwm_divisor * pwm_range)

    wiringpi.pwmWrite(pwm_pin.pin_number, initial_value)


def write_pwm_to_pin_18(value: int):
    """Does what it says on the tin."""
    wiringpi.pwmWrite(18, value)


class PWMPinInfo:
    def __init__(self, pin_number, pwm_range, pwm_clock_divisor):
        self.pwm_range = pwm_range
        self.pin_number = pin_number
        self.pwm_clock_divisor = pwm_clock_divisor
