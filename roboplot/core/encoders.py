"""
This module defines a class to manage encoder activities.

Author: Luke W
"""

import threading

from roboplot.core.gpio.gpio_wrapper import GPIO


class AxisEncoder(threading.Thread):
    """This class is a collection of functions and variables to setup and use an encoder"""

    def __init__(self, pins, positions_per_revolution, distance_per_revolution, thread_name=None):
        """
        Initialises the encoder class.

        Args:
            pins: BCM number of the GPIO pins which make up the A and B channel of the encoder.
                  See pin allocation scheme on google drive.

            positions_per_revolution: the number of counts the encoder has per revolution.

            distance_per_revolution: the linear movement of the axis caused by a full revolution in the transmission.
                                     i.e. in the case of a lead screw, this will be the pitch.
                                     Normalise this to the unit in which you choose to work
        """

        # Initialise thread object (base class initialiser)
        threading.Thread.__init__(self, group=None, target=self.EncoderLoop, name=thread_name)

        # In python, class members appear to be created when you refer to them
        self._positions_per_revolution = positions_per_revolution
        self._distance_per_revolution  = distance_per_revolution

        # Initialise the position to 0 upon creation (may need to be reset on referencing)
        self._count = 0
        self._position = 0

        #setup pins
        for pin in pins:
            GPIO.setup(pin, GPIO.IN)

        #Get easier to remember names for pins
        self._A_Pin = self._gpio_pins[0]
        self._B_Pin = self._gpio_pins[1]

        #Get first encoder pin values
        self._A = GPIO.input(self._A_Pin)
        self._B = GPIO.input(self._B_Pin)

        #setup lock object
        self._lock = threading.Lock()

        #setup exit flag
        self._exitFlag = 0

#    def run(self):
#        """
#        This "Run" function is recommended by online tutorial to prevent starting thread immediately.
#        """
#        return

    def GetPosition(self):
        """
        This function returns the value of the _position variable
        """

        # First, transform count into a linear positio
        self._position = self._distance_per_revolution * self._count / self._positions_per_revolution

        return self._position

    def ResetPosition(self):
        """
        This function resets the position to 0
        """
        self._lock.acquire()

        try:
            self._position = 0
        finally:
            self._lock.release()

    def ExitThread(self):
        """
        This function sets up the conditions to kill the thread

        Shortly after calling this function the thread will exit
        """
        self._lock.acquire()

        try:
            self._exitFlag = 1
        finally:
            self._lock.release()

    def EncoderLoop(self):
        #Note: Not sure if self needs to be passed as a variable to the thread object

        #Infinite while loop until program ends, at which point a flag can be set from another thread
        while(1):
            #Get encoder pin values
            self._A_Prev = self._A
            self._B_Prev = self._B
            self._A = GPIO.input(self._A_Pin)
            self._B = GPIO.input(self._B_Pin)

            #Depending on what changes have occurred, increment or decrement the encoder value
            #Check current and previous values of encoders
            tempcount = 0
            if((self._A == 0) and (self._A_Prev == 0)):
                if((self._B == 1) and (self._B_Prev == 0)):
                    tempcount = tempcount + 1
                if((self._B == 0) and (self._B_Prev == 1)):
                    tempcount = tempcount - 1
            elif((self._A == 1) and (self._A_Prev == 1)):
                if((self._B == 1) and (self._B_Prev == 0)):
                    tempcount = tempcount - 1
                if((self._B == 0) and (self._B_Prev == 1)):
                    tempcount = tempcount + 1

            if((self._B == 0) and (self._B_Prev == 0)):
                if((self._A == 1) and (self._A_Prev == 0)):
                    tempcount = tempcount - 1
                if((self._A == 0) and (self._A_Prev == 1)):
                    tempcount = tempcount + 1
            elif((self._B == 1) and (self._B_Prev == 1)):
                if((self._A == 1) and (self._A_Prev == 0)):
                    tempcount = tempcount + 1
                if((self._A == 0) and (self._A_Prev == 1)):
                    tempcount = tempcount - 1

            # Use a lock to make count variable thread safe
            self._lock.acquire()
            try:
                self._count = self._count + tempcount
            finally:
                self._lock.release()

            #Exit while loop (and consequently kill thread)
            #if exit is requested
            if(self._exitFlag):
                break
