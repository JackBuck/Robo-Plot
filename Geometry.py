#Module to generate motor velocity curves from line inputs

import math

#Generates "Long Line" velocity curve as shown below
#|      ----------
#|     /          \
#|    / |        | \
#|   /              \
#|  /   |        |   \
#| /                  \
#|/     |        |     \
#|-----------------------
#0      D1       D2     D
#
#Alternatively generates a "short line" curve as below
#|      -
#|     / \
#|    / | \
#|   /     \
#|  /   |   \
#| /         \
#|/     |  0   \
#|---------------
#0      D1      D
#
# All units below are in steps, steps/sec or steps/sec^2
#
#Inputs:
#   Vmax - Maximum Speed of motor (i.e. a scalar)
#   Amax - Maximum Acceleration of motor (+ve for speeding up)
#   DecMax - Maximum Deceleration of motor (-ve for slowing down)
#   D    - Distance motor should drive for
#Outputs = [D1, D2, V, Acc, Dec]
#   D1 = Distance to accelerate for
#   D2 = Distance to start decelerating (=D1 for short line )
#   V  = Actual max velocity for motor to go
#   Acc= Actual max acceleration for motor to use (+ve for forwards)
#   Dec= Actual max deceleration for motor to use (-ve for backwards)
def CalcLineDistances(Vmax, Amax, DecMax, D):

    #First check that neither Amax or DecMax are 0's
    if(Amax == 0) or (DecMax == 0):
        return [0,0]

    #Next check whether or not we're travelling a positive or a negative Distance
    #If so, swap the acceleration and deceleration values, and make maximum velocity negative
    if(D < 0):
        Temp = Amax
        Amax = DecMax
        DecMax = Temp
        Vmax = -1 * Vmax

    #Next, determine if this will be a "long" or a "short" line
    Dlim = (Vmax ** 2) * (1 / (2 * Amax) - 1 / (2 * DecMax))
    if(math.fabs(D) < math.fabs(Dlim)):
        #Then this is a short line
        #In which case we won't reach maximum velocity, so recalculate it
        Vmax = math.sqrt(math.fabs((D * 2 * Amax * DecMax / (DecMax - Amax))))
        #Because Vmax is a sqrt, it will always be +ve, so make it -ve if required
        if(D < 0):
            Vmax = Vmax * -1

        #From Vmax, we can calculate D1, which also = D2
        D1 = (Vmax ** 2) / (2 * Amax)

        #For a short line, D2 kind of doesn't exist, so make it the same as D1
        D2 = D1
    else:
        #This is a Long line
        #Calculate D1 first
        D1 = (Vmax ** 2) / (2 * Amax)

        #Then calculate D2
        D2 = D + (Vmax ** 2) / (2 * DecMax)

    return [D1, D2, Vmax, Amax, DecMax]
