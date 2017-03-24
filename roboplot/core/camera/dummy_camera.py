# coding=utf-8
import os
import numpy as np
import cv2
import roboplot.config as config


class DummyCamera:
    """This class holds the functions required to mimic the behavior of the plotter when taking photos."""

    def __init__(self):
        self._conversion_factor = config.Y_PIXELS_TO_MILLIMETRE_SCALE
        self._photo_size_pixels = config.CAMERA_RESOLUTION[0]

        self._map = cv2.imread(config.debug_image_file_path)

        map_width = int(210 / self._conversion_factor)
        map_height = int(297 / self._conversion_factor)
        if self._map is None:
            self._map = np.zeros((map_height, map_width) + (3,), np.uint8)

        # Resize to make it A4 ratio
        self._map = cv2.resize(self._map, (map_width, map_height))
        self._debug_map = self._map.copy()

        # Get width and height. (Should be the same as given above).
        self._map_height = self._map.shape[0]
        self._map_width = self._map.shape[1]

        self._photo_index = 0

    def take_photo_at(self, camera_centre):
        """ This function takes a sub-array representing a photo at the given co-ordinates.
                Args:
                    np.ndarray: An 1x2 matrix representing the global co-ordinates of the picture needed.
                Returns:
                    np.ndarray: An array representing the pixels of the required dummy photo.
                """
        dummy_photo = np.zeros((self._photo_size_pixels, self._photo_size_pixels, 3), np.uint8)

        # Convert the co-ordinates into pixel co-ordinates.
        camera_centre = (int(camera_centre[0] / self._conversion_factor),
                         int(camera_centre[1] / self._conversion_factor))

        # If the photo is near the edge of the paper so that part of the photo will lie outside of the photo this is
        # padded with black so centre is still correct.

        # image min/max are the min/max extents of the pixels required from the map.
        # image min/max placement are the min/max extents of where the sub-array from the map will be positioned in the
        # dummy photo to ensure the dummy photo has correct centre.

        # Set min y value and placement in the photo
        if 0 > camera_centre[0] - int(self._photo_size_pixels / 2):
            image_y_min = 0
            image_y_min_placement = - int(camera_centre[0]) + int(self._photo_size_pixels / 2)
        else:
            image_y_min = int(camera_centre[0]) - int(self._photo_size_pixels / 2)
            image_y_min_placement = 0

        # Set min x value and placement in the photo
        if 0 > int(camera_centre[1]) - int(self._photo_size_pixels / 2):
            image_x_min = 0
            image_x_min_placement = - int(camera_centre[1] + int(self._photo_size_pixels / 2))
        else:
            image_x_min = int(camera_centre[1]) - int(self._photo_size_pixels / 2)
            image_x_min_placement = 0

        # Set max y value and placement in the photo
        if self._map_height < int(camera_centre[0]) + int(self._photo_size_pixels / 2):
            image_y_max = self._map_height
            image_y_max_placement = int(self._photo_size_pixels - (((self._photo_size_pixels / 2) + int(camera_centre[0]))
                                                                   - self._map_height))
        else:
            image_y_max = int(camera_centre[0] + int(self._photo_size_pixels / 2))
            image_y_max_placement = int(self._photo_size_pixels)

        # Set max x value and placement in the photo
        if self._map_width < camera_centre[1] + int(self._photo_size_pixels / 2):
            image_x_max = int(self._map_width)
            image_x_max_placement = int(self._photo_size_pixels - (((self._photo_size_pixels / 2) +
                                                                    camera_centre[1]) - self._map_width))
        else:
            image_x_max = camera_centre[1] + int(self._photo_size_pixels / 2)
            image_x_max_placement = int(self._photo_size_pixels)

        # Get dummy photo as sub array of the map.
        dummy_photo[image_y_min_placement:image_y_max_placement, image_x_min_placement:image_x_max_placement] = \
            self._map[image_y_min:image_y_max, image_x_min:image_x_max]

        if __debug__:
            # Save photo.
            cv2.imwrite(os.path.join(config.debug_output_folder, "Photo_" + str(self._photo_index) + ".jpg"),
                        dummy_photo)

            self._photo_index += 1

            # Show where photos were taken.
            cv2.rectangle(self._debug_map, (image_x_min, image_y_min), (image_x_max, image_y_max), color=(200, 10, 255),
                          thickness=int(2/self._conversion_factor))
            cv2.imwrite(os.path.join(config.debug_output_folder, 'Photo_Positions_Debug.jpg'), self._debug_map)

        return dummy_photo

    @property
    def resolution_mm(self):
        """The size of a photo in pixels"""
        return self.resolution_pixels * self.pixels_to_mm_scale_factors

    @property
    def resolution_pixels(self):
        """The size of a photo in mm"""
        return np.array([self._photo_size_pixels, self._photo_size_pixels])

    @property
    def pixels_to_mm_scale_factors(self):
        return np.array([self._conversion_factor, self._conversion_factor])
