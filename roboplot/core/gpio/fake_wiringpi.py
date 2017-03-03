from roboplot.core.gpio.EmulatorGUI import GPIO as _GPIO


def wiringPiSetupGpio():
    """
    This initialises wiringPi and assumes that the calling program is going to be using the Broadcom GPIO pin
    numbers directly with no re-mapping.

    As above, this function needs to be called with root privileges, and note that some pins are different from
    revision 1 to revision 2 boards.
    """
    _GPIO.setmode(_GPIO.BCM)


# PWM modes
PWM_MODE_MS = 0
PWM_MODE_BAL = 1


def pwmSetMode(mode: int):
    """
    The PWM generator can run in 2 modes – “balanced” and “mark:space”. The mark:space mode is traditional,
    however the default mode in the Pi is “balanced”. You can switch modes by supplying the parameter:
    PWM_MODE_BAL or PWM_MODE_MS.
    """
    assert isinstance(mode, int)


# Pin modes
INPUT = 0
OUTPUT = 1
PWM_OUTPUT = 2
GPIO_CLOCK = 3


def pwmSetRange(range: int):
    """
    This sets the range register in the PWM generator. The default is 1024.

    Notes:
      - I haven't implemented the default range=1024 because I can't test whether it is actually implemented
        as a default parameter in the real wiringpi python wrapper.
    """
    assert isinstance(range, int) and range >= 0


def pinMode(pin: int, mode: int):
    """
    This sets the mode of a pin to either INPUT, OUTPUT, PWM_OUTPUT or GPIO_CLOCK.

    Note that only wiringPi pin 1 (BCM_GPIO 18) supports PWM output and only wiringPi pin 7 (BCM_GPIO 4) supports
    CLOCK output modes.
    """
    _GPIO.setup(pin, mode)


def pwmWrite(pin: int, value: int):
    """
    Writes the value to the PWM register for the given pin. The Raspberry Pi has one on-board PWM pin,
    pin 1 (BMC_GPIO 18, Phys 12) and the range is 0-1024. Other PWM devices may have other PWM ranges.
    """
    assert isinstance(pin, int)
    assert isinstance(value, int)


def pwmSetClock(divisor: int):
    """This sets the divisor for the PWM clock."""
    assert isinstance(divisor, int)
