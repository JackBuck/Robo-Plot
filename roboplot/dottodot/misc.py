"""A module to contain things which, if we had time, would be refactored elsewhere."""

import numpy as np

import roboplot.config as config


def convert_image_point_to_global_coordinates(points, camera_location):
    """Convert points in the image coordinate system to the global coordinate system."""
    # TODO: The camera should take photos which record the camera_location, and scale factors etc.
    # This should be a method on such an image.

    # Convert to numpy object for a clean notation
    points = np.array(points)
    camera_location = np.array(camera_location)
    scale_factors = np.array([config.Y_PIXELS_TO_MILLIMETRE_SCALE, config.X_PIXELS_TO_MILLIMETRE_SCALE])
    camera_resolution = np.array(config.CAMERA_RESOLUTION)

    # Do the computation
    image_centre = camera_resolution / 2
    return camera_location + scale_factors * (points - image_centre)
