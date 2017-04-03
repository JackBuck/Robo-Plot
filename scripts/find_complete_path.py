import roboplot.core.hardware as hardware
import roboplot.imgproc.start_end_detection as start_end_detection
import roboplot.imgproc.image_analysis as image_analysis
import roboplot.imgproc.path_following as path_following
from roboplot.core.gpio.gpio_wrapper import GPIO

try:
    # Home axes.
    hardware.plotter.home()

    global_centre = start_end_detection.find_green_triangle(20)
    centre, photo = start_end_detection.find_green_centre(global_centre, 20)

    a_path_finder = path_following.PathFinder()
    computed_camera_path = a_path_finder.compute_complete_path(photo, centre)


finally:
    GPIO.cleanup()

print("Done")


