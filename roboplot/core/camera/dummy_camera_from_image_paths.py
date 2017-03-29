import cv2
import numpy as np


class DummyCameraFromImagePaths:
    def __init__(self, resolution_pixels_xy: (int, int), pixels_to_mm_scale_factors_xy: (float, float),
                 image_paths, default_image_colour: (int, int, int) = (255, 255, 255)):
        """
        Args:
            resolution_pixels_xy (int, int):
            pixels_to_mm_scale_factors_xy (float, float):
            image_paths (list[str]):
            default_image_colour (int, int, int):
        """
        self._resolution_pixels_xy = np.array(resolution_pixels_xy)
        self._pixels_to_mm_scale_factors_xy = np.array(pixels_to_mm_scale_factors_xy)
        self._image_paths = image_paths
        self._default_image_colour = np.reshape(default_image_colour, [1, 1, 3]).astype(np.uint8)
        self._photo_index = 0

    def take_photo_at(self, camera_centre: any) -> np.ndarray:
        print('Taking photo at ({0[0]}, {0[1]}):'.format(camera_centre))

        if self._photo_index < len(self._image_paths):
            print(self._image_paths[self._photo_index])
            img = cv2.imread(self._image_paths[self._photo_index])
            img = cv2.resize(img, tuple(self.resolution_pixels_xy))
            self._photo_index += 1
            return img
        else:
            print('Default image')
            return self._default_image_colour * np.ones(self.resolution_pixels_xy, dtype=np.uint8)

    @property
    def resolution_mm_xy(self):
        """The size of a photo in mm"""
        return self.resolution_pixels_xy * self.pixels_to_mm_scale_factors_xy

    @property
    def resolution_pixels_xy(self):
        """The size of a photo in pixels"""
        return self._resolution_pixels_xy

    @property
    def pixels_to_mm_scale_factors_xy(self):
        """Two numbers (y,x), which when multiplied by """
        return self._pixels_to_mm_scale_factors_xy
