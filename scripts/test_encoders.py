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
    parser.add_argument('-a', '--axis', default='X',
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
    test_axis.current_location = 0

    # Check at right location
    assert test_axis.current_location == 0, 'Reset Encoder Position Failed (current_location != 0).'
    assert test_axis.expected_location == 0, 'Reset Encoder Position Failed (expected_location != 0).'

    # calculate steps per millimetre (useful later) and required steps
    steps_per_milli = 200 / 8
    counts_per_milli = 96 / 8
    required_steps = args.length * steps_per_milli

    # check if we need to go backwards or forwards?
    backwards = False
    if required_steps < 0:
        required_steps *= -1
        backwards = True

    test_axis.forwards = not backwards

    # calculate sleep time
    totaltime = args.length / args.pen_millimetres_per_second
    sleeptime = totaltime / required_steps

    # run for the required number of steps
    for i in range(int(required_steps)):
        test_axis.step()
        time.sleep(sleeptime)

    # calculate expected distance
    expected_distance = test_axis.expected_location
    encoder_distance = test_axis.current_location

    # print the distances for comparison
    print('Expected Distance (from motor): ', end='')
    print(expected_distance)
    print('Expected Distance (from encoder): ', end='')
    print(encoder_distance)


finally:
    hardware.cleanup()
