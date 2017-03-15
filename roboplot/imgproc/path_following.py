import operator
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis


def convert_to_global_coords(points, scan_direction, camera_position):

    # Scale factors
    x_scaling = config.X_PIXELS_TO_MILLIMETRE_SCALE
    y_scaling = config.Y_PIXELS_TO_MILLIMETRE_SCALE

    offset = config.CAMERA_RESOLUTION[0]/2

    # Rotate and scale points to global orientation.
    if scan_direction is image_analysis.Direction.SOUTH:
        output_points = [tuple(map(operator.add, camera_position, (y * y_scaling, (x - offset) * x_scaling)))
                         for (y, x) in points]
    elif scan_direction is image_analysis.Direction.EAST:
        output_points = [tuple(map(operator.add, camera_position, (-(x - offset) * x_scaling, y * y_scaling)))
                         for (y, x) in points]
    elif scan_direction is image_analysis.Direction.WEST:
        output_points = [tuple(map(operator.add, camera_position, ((x - offset) * x_scaling, -y * y_scaling)))
                         for (y, x) in points]
    else:
        output_points = [tuple(map(operator.add, camera_position, (-y * y_scaling, -(x - offset) * x_scaling)))
                         for (y, x) in points]

    return output_points
