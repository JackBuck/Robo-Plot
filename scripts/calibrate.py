import context
import cv2


import roboplot.config as config
from roboplot.core.gpio.gpio_wrapper import GPIO
import roboplot.core.camera.camera_wrapper as camera_wrapper
import roboplot.imgproc.colour_detection as cd
import roboplot.core.hardware as hardware


try:
    a_camera = camera_wrapper.Camera()
    photo = a_camera.take_photo_at((60, 20))
    hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
    hsv_image[:, :, 2]= cv2.medianBlur(hsv_image[:, :, 2], ksize=5)
    hsv_image[:, :, 2] = cv2.adaptiveThreshold(hsv_image[:, :, 2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=11, C=2)
    (cX, cY) = cd.detect_black(hsv_image, 0, False)

    if cX != -1:
        # For some reason objects to putting this on a rotated image.??
        #cv2.circle(photo, (cX, cY), 2, (255, 10, 10), 1)
        cv2.imshow('Centre', cv2.resize(photo, (500, 500)))
        cv2.waitKey(0)
        print("Point Found")

        print(cY)
        print(cX)
        target_location = [hardware.plotter._axes.current_location[0] + (cY - photo.shape[0]/2) * config.Y_PIXELS_TO_MILLIMETRE_SCALE,
                           hardware.plotter._axes.current_location[1] + (cX - photo.shape[1]/2) * config.X_PIXELS_TO_MILLIMETRE_SCALE]

        print('Current' + str(hardware.plotter._axes.current_location))
        print('Target' + str(target_location))
        hardware.plotter.move_pen_to(target_location)

        photo = a_camera.take_photo_at((60, 20))

        hsv_image = cv2.cvtColor(photo, cv2.COLOR_BGR2HSV)
        hsv_image[:, :, 2] = cv2.medianBlur(hsv_image[:, :, 2], ksize=5)
        hsv_image[:, :, 2] = cv2.adaptiveThreshold(hsv_image[:, :, 2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=11, C=2)
        (cX, cY) = cd.detect_black(hsv_image, 0, False)

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



