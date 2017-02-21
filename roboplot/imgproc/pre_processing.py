import numpy as np
import cv2
import enum
import os
import math
import time

import roboplot.core.config


class PreProcessing:
    def __init__:
        self._processed_image_index = 0
    
    @staticmethod
    def global_threshold:
        _, processed_image = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'GlobalProcessedImage_' + str(self._processed_image_index), processed_image)
            self._processed_image_index += 1
            
    return processed_image
    
    @staticmethod
    def otsu_threshold:
        _, processed_image = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'OtsuProcessedImage_' + str(self._processed_image_index), processed_image)
            self._processed_image_index += 1
            
    return processed_image
    
    @staticmethod
    def gauss_otsu_threshold:
        blur = cv2.GaussianBlur(img,(5,5),0)
        _, processed_image = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        if __debug__:
            cv2.imwrite(config.debug_output_folder + 'OtsueGaussProcessedImage_' + str(self._processed_image_index), processed_image)
            self._processed_image_index += 1
            
    return processed_image