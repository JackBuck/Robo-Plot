import threading
import wiringpi as wiringpi

#Constant definitions
A_CHANNEL_GPIO   = 0
B_CHANNEL_GPIO   = 1

#globals
Count = 0
A_Prev = 0
B_Prev = 0

#Function to be a callback for when any of the encoder interrupts fire
#Conveniently the
def EncoderCallback():

    global A_Prev
    global B_Prev
    global Count

    #Get current encoder values
    A = wiringpi.digitalRead(A_CHANNEL_GPIO)
    B = wiringpi.digitalRead(B_CHANNEL_GPIO)

    #Check current and previous values of encoders
    tempcount = 0
    if((A == 0) and (A_Prev == 0)):
        if((B == 1) and (B_Prev == 0)):
            tempcount = tempcount + 1
        if((B == 0) and (B_Prev == 1)):
            tempcount = tempcount - 1
    elif((A == 1) and (A_Prev == 1)):
        if((B == 1) and (B_Prev == 0)):
            tempcount = tempcount - 1
        if((B == 0) and (B_Prev == 1)):
            tempcount = tempcount + 1

    if((B == 0) and (B_Prev == 0)):
        if((A == 1) and (A_Prev == 0)):
            tempcount = tempcount - 1
        if((A == 0) and (A_Prev == 1)):
            tempcount = tempcount + 1
    elif((B == 1) and (B_Prev == 1)):
        if((A == 1) and (A_Prev == 0)):
            tempcount = tempcount + 1
        if((A == 0) and (A_Prev == 1)):
            tempcount = tempcount - 1

    A_Prev = A
    B_Prev = B

    Count = Count + tempcount

def EncoderLoop():
    while(1):
        EncoderCallback()

wiringpi.wiringPiSetupGpio()            #Setup wiringpi
wiringpi.pinMode(A_CHANNEL_GPIO, wiringpi.INPUT) #Setup both channels as inputs
wiringpi.pinMode(B_CHANNEL_GPIO, wiringpi.INPUT)

#Get initial values
A_Prev = wiringpi.digitalRead(A_CHANNEL_GPIO)
B_Prev = wiringpi.digitalRead(B_CHANNEL_GPIO)

#Set up second thread to deal with encoders
t = threading.Thread(target=EncoderLoop)
t.start()

#infinite loop printing to the screen
while(1):
    #EncoderCallback()

    print("{0:06}".format(Count), end='\r')
