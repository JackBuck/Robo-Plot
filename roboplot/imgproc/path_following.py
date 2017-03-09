import operator
import roboplot.config as config
import roboplot.imgproc.image_analysis as image_analysis


def convert_to_global_coords(points, scan_direction, camera_position):

    # Scale factors
    x_scaling = config.x_pixels_to_points_scale  # (based on a 200x200 pixel photo of a 40mm square)
    y_scaling = config.y_pixels_to_points_scale  # (based on a 200x200 pixel photo of a 40mm square)

    # Rotate and scale points to global orientation.
    if scan_direction is image_analysis.Direction.SOUTH:
        output_points = [tuple(map(operator.add, camera_position, (y * y_scaling, x * x_scaling))) for (y, x) in points]
    elif scan_direction is image_analysis.Direction.EAST:
        output_points = [tuple(map(operator.add, camera_position, (-x * x_scaling, y * y_scaling))) for (y, x) in points]
    elif scan_direction is image_analysis.Direction.WEST:
        output_points = [tuple(map(operator.add, camera_position, (x * x_scaling, -y * y_scaling))) for (y, x) in points]
    else:
        output_points = [tuple(map(operator.add, camera_position, (-y * y_scaling, -x * x_scaling))) for (y, x) in points]

    return output_points
