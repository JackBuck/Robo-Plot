import unittest
from Motor import Motor
from EmulatorGUI import GPIO
import time

#Each set of tests can be in their own class, but it much deriv from unnit.TestCase
class MotorTest(unittest.TestCase):

    #Each test has its own function here. There are lots of different functions to use in tests see
    def testPass(self):
        self.failUnless(True)

    def testConstructor(self):
        # Set GPIO mode.
        GPIO.setmode(GPIO.BCM)

        # Define inputs
        input_pins = [17, 22, 23, 24]
        input_sequence = [[1,0,1,0],[0,1,1,0],[0,1,0,1],[1,0,0,1]]
        input_rps = 10.0

        #Construct Motor
        a_motor = Motor(input_pins, input_sequence, input_rps)

        #Check motor has been assigned correctly
        output_pins = a_motor.GPIO_pins
        self.failUnlessEqual(input_pins, output_pins)
        output_rps = a_motor.rps
        self.failUnlessEqual(input_rps, output_rps)
        output_sequence = a_motor.sequence
        self.failUnlessEqual(input_sequence, output_sequence)
        self.failUnless(a_motor.Clockwise)

        GPIO.cleanup(self)



    def testStep(self):
        # Set GPIO mode.
        GPIO.setmode(GPIO.BCM)

        #Define and construct Motor
        input_pins = [17, 22, 23, 24]
        input_sequence = [[1, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 1], [1, 0, 0, 1]]
        input_rps = 10.0
        a_motor = Motor(input_pins, input_sequence, input_rps)

        a_motor.step()

        # Check it works for 10 step cycles.
        for step in range(0,10):

            # Check each pin is correct after each step.
            for pin in range(0,4):

                current_pin = input_pins[pin]
                pin_status = GPIO.input(current_pin)
                current_step = step %4
                correct_status = (input_sequence[step %4][pin] == 1)
                self.failUnless(pin_status == correct_status)

            if a_motor.Clockwise:
                next_step = (step+1) % 4
            else:
                next_step = (step-1) % 4

            self.failUnless(a_motor.next_step == next_step)

            # Optional delay to visually see the changes.
            time.sleep(1)

            a_motor.step()


        GPIO.cleanup(self)
# You need to close the GPIO window to complete the tests.



#Running this runs all the tests and outputs their results.
def main():
    unittest.main()

if __name__ == '__main__':
    main()