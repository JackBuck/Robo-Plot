import numpy as np
import cv2
import enum
import os
import math
import time


import roboplot.config as config


class PreProcessing:
    def __init__(self):
        self._processed_image_index = 0
    
    def global_threshold(self, img):
        _, processed_image = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'GlobalProcessedImage_' + str(self._processed_image_index) + '.jpg', processed_image)
            self._processed_image_index += 1
            
        return processed_image
    
    def otsu_threshold(self, img):
        _, processed_image = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'OtsuProcessedImage_' + str(self._processed_image_index) + '.jpg', processed_image)
            self._processed_image_index += 1
            
        return processed_image
    
    def gauss_otsu_threshold(self, img):
        blur = cv2.GaussianBlur(img,(20,20),0)
        _ , processed_image = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'OtsuGaussProcessedImage_' + str(self._processed_image_index) + '.jpg', processed_image)
            self._processed_image_index += 1
            
        return processed_image
    
    def erosion(self, img):
        kernel = np.ones((5,5),np.uint8)
        processed_image = cv2.erode(img,kernel,iterations = 1)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'ErodedProcessedImage_' + str(self._processed_image_index) + '.jpg', processed_image)
            self._processed_image_index += 1
            
        return processed_image
        
        