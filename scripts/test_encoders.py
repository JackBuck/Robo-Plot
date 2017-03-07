#!/usr/bin/env python3

import argparse
import time

import context
import roboplot.core.hardware as hardware

try:
    # Commandline arguments
    parser = argparse.ArgumentParser(description='Test Encoders VS Motors.')
    parser.add_argument('-l', '--length', type=float, default=100,
                        help='the length of the test line in millimetres (default: %(default)smm)')
    parser.add_argument('-a', '--axis', type=str, choices=('X', 'Y'), nargs='?', default='X',
                        help='the axis to test upon (default: %(default)s)')
    parser.add_argument('-s', '--speed', metavar='SPEED', dest='pen_millimetres_per_second', type=float, default=32,
                        help='the target speed for the pen in millimetres per second (default: %(default)smm/s)')

    args = parser.parse_args()

    # Get the appropriate axis and motor
    if args.axis == 'X':
        test_axis = hardware.x_axis
    elif args.axis == 'Y':
        test_axis = hardware.y_axis
    else:
        raise ValueError('Bad axis option. Choose X or Y.')

    # Reset the soft positions of motors and encoders to zero
    forced_initial_location = 100  # To get around pretend limit switches when running with simulated hardware
    test_axis.current_location = forced_initial_location

    # Check at right location
    assert test_axis.current_location == forced_initial_location, \
        'Reset Encoder Position Failed (current_location != {}).'.format(forced_initial_location)
    assert test_axis.expected_location == forced_initial_location,\
        'Reset Encoder Position Failed (expected_location != {}).'.format(forced_initial_location)

    # calculate steps per millimetre (useful later) and required steps
    required_steps = args.length / test_axis.millimetres_per_step

    # check if we need to go backwards or forwards?
    test_axis.forwards = required_steps >= 0
    required_steps = abs(required_steps)

    # calculate sleep time
    totaltime = abs(args.length) / args.pen_millimetres_per_second
    sleeptime = totaltime / required_steps

    # run for the required number of steps
    for i in range(int(required_steps)):
        test_axis.step()
        time.sleep(sleeptime)

    # calculate expected distance
    time.sleep(0.5)  # To give the steppers time to settle (nb this should be masses more than we need!)
    expected_distance = test_axis.expected_location - forced_initial_location
    encoder_distance = test_axis.current_location - forced_initial_location

    # print the distances for comparison
    print('Requested Distance: ', end='')
    print(args.length)
    print('Expected Distance (from motor): ', end='')
    print(expected_distance)
    print('Expected Distance (from encoder): ', end='')
    print(encoder_distance)


finally:
    hardware.cleanup()
