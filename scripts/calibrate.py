import context
import cv2
import argparse
import numpy as np

import roboplot.config as config
from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.colour_detection as cd
import roboplot.core.curves as curves
import roboplot.core.hardware as hardware


try:
    a_camera = camera_wrapper.Camera()
    photo = a_camera.take_photo_at((0 ,0))

    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
    (cX, cY) = cd.detect_green(hsv_image, 0, False)

    if cX != -1:
        cv2.circle(photo, (cX, cY), 2, (255, 10, 10), 1)
        cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)
        print("Point Found")

        target_location = [hardware.both_axes.current_location[0] + cX * config.X_PIXELS_TO_MILLIMETRE_SCALE,
                           hardware.both_axes.current_location[1] + cY * config.Y_PIXELS_TO_MILLIMETRE_SCALE]

        line_segment = curves.LineSegment(hardware.both_axes.current_location, target_location)
        hardware.both_axes.follow(curve=line_segment, pen_speed=np.Inf)

        photo = a_camera.take_photo_at((0, 0))
        hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
        (cX, cY) = cd.detect_green(hsv_image, 2, False)

        cv2.imshow('Centre2', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)

        print(cY)
        print(cX)

    else:
        cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)
        print("Point Not Found")

finally:
    GPIO.cleanup()



