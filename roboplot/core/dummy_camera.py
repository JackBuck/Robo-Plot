# coding=utf-8
import numpy as np
import cv2

global debug

class DummyCamera:
    """This class holds the functions required to mimic the behavior of the plotter when taking photos."""

    def __init__(self):
        file_path = '../../resources/Challenge_2_Test_Images/HackspacePath_Sample.png'
        self._map = cv2.imread(file_path)


        #Resize to make it A4 ratio with 40mm = 200 pixels
        self._map = cv2.resize(self._map, (5940, 4200))
        self.debug_map = self._map.copy()


        # Get width and height. (Should be the same as given above.
        self._map_width = self._map.shape[0]
        self._map_height = self._map.shape[1]

        self.conversion_factor = 0.2 # This converts pixels to mm, 1mm  is 5 pixels
        self._photo_size = 200

    def take_photo_at(self, camera_centre):
        """ This function takes a sub-array representing a photo at the given co-ordinates.
                Args:
                    np.ndarray: An 1x2 matrix representing the global co-ordinates of the picture needed.
                Returns:
                    np.ndarray: An array representing the pixels of the required dummy photo.
                """
        dummy_photo = np.zeros((self._photo_size, self._photo_size, 3), np.uint8)

        # Convert the co-ordinates into pixel co-ordinates.
        camera_centre *= self._conversion_factor

        # If the photo is near the edge of the paper so that part of the photo will lie outside of the photo this is
        # padded with black so centre is still correct.

        # image min/max are the min/max extents of the pixels required from the map.
        # image min/max placement are the min/max extents of where the sub-array from the map will be positioned in the
        # dummy photo to ensure the dummy photo has correct centre.


        # Set min x value and placement in the photo
        if 0 > camera_centre[0] - int(self._photo_size / 2):
            image_x_min = 0
            image_x_min_placement = - camera_centre[0]
        else:
            image_x_min = camera_centre[0] - int(self._photo_size / 2)
            image_x_min_placement = 0

        # Set min y value and placement in the photo
        if 0 > camera_centre[1] - int(self._photo_size / 2):
            image_y_min = 0
            image_y_min_placement = - (camera_centre[1] + int(self._photo_size / 2))
        else:
            image_y_min = camera_centre[1] - int(self._photo_size / 2)
            image_y_min_placement = 0

        # Set max x value and placement in the photo
        if self._map_width < camera_centre[0] + int(self._photo_size / 2):
            image_x_max = self._map_width
            image_x_max_placement = int(self._photo_size - (((self._photo_size / 2) + camera_centre[0]) - self._map_width))
        else:
            image_x_max = int(camera_centre[0] + int(self._photo_size / 2))
            image_x_max_placement = int(self._photo_size)

        # Set max y value and placement in the photo
        if self._map_height < camera_centre[1] + int(self._photo_size / 2):
            image_y_max = int(self._map_height)
            image_y_max_placement = int(self._photo_size - (((self._photo_size / 2) + camera_centre[1]) - self._map_height))
        else:
            image_y_max = int(camera_centre[1] + int(self._photo_size / 2))
            image_y_max_placement = int(self._photo_size)

        # Get dummy photo as sub array of the map.
        dummy_photo[image_y_min_placement:image_y_max_placement, image_x_min_placement:image_x_max_placement] = \
            self._map[image_y_min:image_y_max, image_x_min:image_x_max]

        if debug:
            cv2.imshow('Dummy Photo', cv2.resize(dummy_photo, (200, 200)))

        return dummy_photo

