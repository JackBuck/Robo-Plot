# coding=utf-8
import os
import numpy as np
import cv2
import roboplot.config as config



class DummyCamera:
    """This class holds the functions required to mimic the behavior of the plotter when taking photos."""

    def __init__(self):
        self._map = cv2.imread(config.debug_image_file_path)

        if self._map is None:
            self._map = np.zeros((4200, 5940) + (3,), np.uint8)

        # Resize to make it A4 ratio with 40mm = 200 pixels
        self._map = cv2.resize(self._map, (4200, 5940))
        self._debug_map = self._map.copy()

        # Get width and height. (Should be the same as given above).
        self._map_width = self._map.shape[0]
        self._map_height = self._map.shape[1]

        self._conversion_factor = 0.05  # This converts pixels to mm, 1mm  is 20 pixels
        self._photo_size = 800
        self._photo_index = 0

    def take_photo_at(self, camera_centre):
        """ This function takes a sub-array representing a photo at the given co-ordinates.
                Args:
                    np.ndarray: An 1x2 matrix representing the global co-ordinates of the picture needed.
                Returns:
                    np.ndarray: An array representing the pixels of the required dummy photo.
                """
        dummy_photo = np.zeros((self._photo_size, self._photo_size, 3), np.uint8)

        # Convert the co-ordinates into pixel co-ordinates.
        camera_centre = (int(camera_centre[0] / self._conversion_factor),
                         int(camera_centre[1] / self._conversion_factor))

        # If the photo is near the edge of the paper so that part of the photo will lie outside of the photo this is
        # padded with black so centre is still correct.

        # image min/max are the min/max extents of the pixels required from the map.
        # image min/max placement are the min/max extents of where the sub-array from the map will be positioned in the
        # dummy photo to ensure the dummy photo has correct centre.

        # Set min x value and placement in the photo
        if 0 > camera_centre[0] - int(self._photo_size / 2):
            image_x_min = 0
            # Simplification of int(self._photo_size - (camera_centre[0] + int(self._photo_size/2)))
            image_x_min_placement = int(self._photo_size/2) - int(camera_centre[0])
        else:
            image_x_min = int(camera_centre[0]) - int(self._photo_size / 2)
            image_x_min_placement = 0

        # Set min y value and placement in the photo
        if 0 > int(camera_centre[1]) - int(self._photo_size / 2):
            image_y_min = 0
            image_y_min_placement = int(self._photo_size/2) - int(camera_centre[1])
        else:
            image_y_min = int(camera_centre[1]) - int(self._photo_size / 2)
            image_y_min_placement = 0

        # Set max x value and placement in the photo
        if self._map_width < int(camera_centre[0]) + int(self._photo_size / 2):
            image_x_max = self._map_width
            image_x_max_placement = int(self._photo_size / 2 - camera_centre[0] + self._map_width)
        else:
            image_x_max = int(camera_centre[0] + int(self._photo_size / 2))
            image_x_max_placement = int(self._photo_size)

        # Set max y value and placement in the photo
        if self._map_height < camera_centre[1] + int(self._photo_size / 2):
            image_y_max = int(self._map_height)
            image_y_max_placement = int(self._photo_size / 2 - camera_centre[1] + self._map_height)
        else:
            image_y_max = camera_centre[1] + int(self._photo_size / 2)
            image_y_max_placement = int(self._photo_size)

        # Get dummy photo as sub array of the map.
        dummy_photo[image_x_min_placement:image_x_max_placement, image_y_min_placement:image_y_max_placement] = \
            self._map[image_x_min:image_x_max, image_y_min:image_y_max]

        if __debug__:
            # Save photo.
            cv2.imwrite(os.path.join(config.debug_output_folder, "Photo_" + str(self._photo_index) + ".jpg"),
                        dummy_photo)

            self._photo_index += 1

            # Show where photos were taken.
            cv2.rectangle(self._debug_map, (image_y_min, image_x_min), (image_y_max, image_x_max), (200, 10, 255), 40)
            cv2.imwrite(os.path.join(config.debug_output_folder, 'Photo_Positions_Debug.jpg'), self._debug_map)

        return dummy_photo

