import RPi.GPIO as GPIO

#Constant definitions
A_CHANNEL_GPIO   = 0
B_CHANNEL_GPIO   = 1

#globals
Count = 0
A_Prev = 0
B_Prev = 0
CheckFlag = False

def EncoderCallback(channel):
    #Flag to let main program know the encoder has changed
    global CheckFlag
    CheckFlag = True

#Function to be a callback for when any of the encoder interrupts fire
#Conveniently the
def CheckEncoder():

    global A_Prev
    global B_Prev
    global Count

    #Get current encoder values
    A = GPIO.input(A_CHANNEL_GPIO)
    B = GPIO.input(B_CHANNEL_GPIO)

    #Check current and previous values of encoders
    tempcount = 0
    if((A == 0) and (A_Prev == 0)):
        if((B == 1) and (B_Prev == 0)):
            tempcount = tempcount + 1
        elif((B == 0) and (B_Prev == 1)):
            tempcount = tempcount - 1
    elif((A == 1) and (A_Prev == 1)):
        if((B == 1) and (B_Prev == 0)):
            tempcount = tempcount - 1
        if((B == 0) and (B_Prev == 1)):
            tempcount = tempcount + 1

    if((B == 0) and (B_Prev == 0)):
        if((A == 1) and (A_Prev == 0)):
            tempcount = tempcount - 1
        elif((A == 0) and (A_Prev == 1)):
            tempcount = tempcount + 1
    elif((B == 1) and (B_Prev == 1)):
        if((A == 1) and (A_Prev == 0)):
            tempcount = tempcount + 1
        if((A == 0) and (A_Prev == 1)):
            tempcount = tempcount - 1

    A_Prev = A
    B_Prev = B

    Count = Count + tempcount

GPIO.setmode(GPIO.BCM)            #Setup wiringpi
GPIO.setup(A_CHANNEL_GPIO, GPIO.IN)
GPIO.setup(B_CHANNEL_GPIO, GPIO.IN) #Setup both channels as inputs

#Get initial values
A_Prev = GPIO.input(A_CHANNEL_GPIO)
B_Prev = GPIO.input(B_CHANNEL_GPIO)

#Attach interrupt callback
GPIO.add_event_detect(A_CHANNEL_GPIO, GPIO.BOTH, callback=EncoderCallback)
GPIO.add_event_detect(B_CHANNEL_GPIO, GPIO.BOTH, callback=EncoderCallback)

#infinite loop printing to the screen
while(1):
    if(CheckFlag == True):
        CheckEncoder()
        CheckFlag = False

    print("{0:06}".format(Count), end='\r')
