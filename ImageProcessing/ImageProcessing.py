from enum import Enum
from PIL import Image
from PIL import ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import math
import time

debug = True
global white_threshold
white_threshold = 130

class Direction(Enum):
    North = 0
    East  = 1
    South = 2
    West  = 3

class PathAnalyser:

    """This class is holds the information to analyse the path."""

    def __init__(self, starting_position, starting_direction):

        """

        Initialises the Path Analyser Class.

        Args:

            starting_position: The starting position, previously determined by finding the green triangles.

            starting_direction: The direction to scan in based on where the starting position was found.

        """

        self._path = [starting_position]

        self._scan_direction = starting_direction


    def find_start_position(self):

        #Home to known point

        # Cycle round extents of picture.

        # Get Image (either from camera or loaded image)

        # Analyse for green triangle

        #If found



class ImageAnalyser:
    """This class is holds the information to analyse the path."""

    def __init__(self, file_path, scan_direction):

        """

        Initialises the Image Analyser Class.

        Args:

            file_location: The location of the file to be analysed.

        """

        self._scan_direction = scan_direction
        self._original_image = Image.open(file_path)

        # Currently resize the image this may be taken out if the photos are taken small enough
        # The actual size of the converted function may also be modified.

        self._width = 200
        self._height = 200
        self._processed_img = self._original_image.resize((self._width, self._height))

        # Convert image to black and white - we cannot take the photos in black and white as we
        # must first search for the red triangle.
        self._processed_img = self._processed_img.convert('L')

        # Put pixels into an array for processing
        self._pixels = np.asarray(self._processed_img)


        if scan_direction == Direction.North:
            self._pixels = self._pixels
        elif scan_direction == Direction.East:
            self._pixels = np.rot90(self._pixels)
        elif scan_direction == Direction.South:
            self._pixels = np.rot90(self._pixels, 2)
        elif scan_direction == Direction.West:
            self._pixels = np.rot90(self._pixels, 3)

        #Create an image with which to display computed values
        self._debugimage = self._processed_img.convert('RGB')
        self._debugpixels = np.asarray(self._debugimage)

        # Currently a simple tolerance is used based on the size of the image - this is assuming a
        # rough view of 50 x 50 mm^2.
        self._tol = min((self._width / 3), (self._height / 3))


    def compute_weighted_centroid(lightnesses):
        num_elements = lightnesses.shape
        np.savetxt('Lightnesses.txt', lightnesses, fmt="%2.1f", delimiter=',')

        x = np.arange(num_elements[0])
        is_white = lightnesses > white_threshold
        num_white = sum(is_white)
        weighted = np.multiply(is_white, x)
        np.savetxt('weight.txt', weighted, fmt="%2.1f", delimiter=" , ")

        if num_white == 0:
            return -1
        else:
            flt_centroid = sum(is_white * x) / num_white

        return int(flt_centroid)


    def AnalyseImage(self):

        #Get average pixel positions.
        (x_indices, y_indices) = np.array(self.AnalyseRow())

        #Approximate the pixels with a line.
        segments = [0, len(x_indices)-1]
        lines = []
        segment_index = 0
        tol = 3



        while segments[segment_index] < len(x_indices)-1:
            lowest_index_error = 1
            upper_bound = segments[segment_index + 1]
            while lowest_index_error != -1:
                start_index = segments[segment_index]
                end_index = upper_bound + 1


                # Set the start point of the line to the centre 0,0 or the end of the last line calculated.
                if len(lines):
                    start_point = (y_indices[start_index], y_indices[start_index]*lines[-1][0] + lines[-1][1])
                else:
                    start_point = (0,0)

                #Approximate this interval with a line

                y_subset = y_indices[start_index: end_index]

                x_subset = x_indices[start_index: end_index]

                current_line = InterpolateAverages.ApproximateWithLine(start_point, y_indices[start_index: end_index], x_indices[start_index: end_index])

                # Determine the index at which the distance to the line first exceeds the tolerance. If no index exceeds the tolerance
                # this returns -1.

                lowest_index_error = InterpolateAverages.ErrorFromLine(current_line, y_indices[start_index: end_index], x_indices[start_index: end_index], tol)


                if lowest_index_error != -1:
                    # Shorten the interval to end at the first point the error became to great.
                    # Modify the lowest index to a global index.
                    lowest_index = lowest_index_error + start_index

                    # Split the interval one before the max error this ensures there is a line approximating these
                    # points which is within tolerance of th whole line.
                    upper_bound = lowest_index - 1
                else:
                    # Add this line to the list of lines.
                    segments.insert(segment_index + 1, upper_bound)
                    lines.append(current_line)


            # Show current state if debug is set to true.
            #if (debug):
                #self.ShowApproximation(lines, segments, y_indices)

            # Good approximation found for this interval move to next interval.
            segment_index += 1


        # Show current state if debug is set to true.
        if(debug):
            self.ShowApproximation(lines, segments, y_indices)


    def ShowApproximation(self, lines, segments, y_indices):

        """ Displays the line segments x = my + c on image"""


        #Creat copy of image with averages marked on.

        image = self._debugimage

        # Set centre of image.

        #image = image.resize((500, 500))
        centre = (100, 100)

        factor = 1


        #For each line segment draw a line between the start and end points of the segment and mark the start and end
        # with a circle.

        for current_line in range(0, len(lines)):
            (m, c) = lines[current_line]


            # Compute start co - ordinates of line segment.
            y_start_cart = y_indices[segments[current_line]]
            x_start_cart = (y_start_cart * m) + c

            x_start_cart = round(x_start_cart * factor)
            y_start_cart = round(y_start_cart * factor)
            (x_start_image, y_start_image) = ImageAnalyser.ConvertToImageCoOrds(x_start_cart, y_start_cart, centre, self._scan_direction)


            # Compute end co - ordinate of line segment.
            y_end_cart = y_indices[segments[current_line + 1]]
            x_end_cart = (y_end_cart * m) + c

            y_end_cart = round(y_end_cart * factor)
            x_end_cart = round(x_end_cart * factor)
            (x_end_image, y_end_image) = ImageAnalyser.ConvertToImageCoOrds(x_end_cart, y_end_cart, centre, self._scan_direction)

            #Add artifacts to image
            draw = ImageDraw.Draw(image)

            draw.line([x_start_image, y_start_image, x_end_image, y_end_image], (50, 100, 240), 1)
            draw.ellipse((x_start_image - 1, y_start_image - 1, x_start_image + 1, y_start_image + 1), fill = 'blue', outline='blue')
            draw.ellipse((x_end_image - 1, y_end_image - 1, x_end_image + 1, y_end_image + 1), fill = 'blue', outline='blue')

            del draw

        image.show()

    def ConvertToImageCoOrds(x, y, centre, scan_direction):
        if (scan_direction == Direction.North):
            x_image = centre[0] + x
            y_image = centre[1] - y
        elif (scan_direction == Direction.East):
            x_image = centre[1] + y
            y_image = centre[0] + x
        elif (scan_direction == Direction.South):
            x_image = centre[0] - x
            y_image = y + centre[1]
        elif (scan_direction == Direction.West):
            x_image = centre[1] - y
            y_image = centre[0] - x

        return (x_image, y_image)


    def AnalyseRow(self):
        average_index_rows = []
        y_indices = []
        y_indices.append(0)
        average_index_rows.append(0)

        increment = -1
        end_index = 0

        count = 1
        for rr in range(int(self._height/2), end_index, increment):

            #Determine the indices to average based on the last valid index.
            min_index = int(max(0, average_index_rows[-1]-self._tol + self._width/2))
            max_index = int(min(self._height, average_index_rows[-1] + self._tol + self._width/2))

            sub_array = self._pixels[ rr, min_index:max_index]
            centroid = ImageAnalyser.compute_weighted_centroid(sub_array)
            last_index_invalid = False

            if centroid != -1:
                next_centroid = min_index + ImageAnalyser.compute_weighted_centroid(sub_array) - self._width/2
            else:
                next_centroid = -1

            if (count == 1) or abs(next_centroid - average_index_rows[-1]) < 3:
                average_index_rows.append(next_centroid)
                y_indices.append(count)
                last_index_invalid = False

            else:
                if last_index_invalid:
                    #We have 2 invalid entries in a row. This means the approximation should stop.
                    break

                last_index_invalid = True

            count += 1

        if debug:
            self.ShowDebugAverageRows(average_index_rows, y_indices)

            return average_index_rows, y_indices


    def ShowDebugAverageRows(self, average_index_rows, y_indices):

        img_pixels = self._debugimage.load()
        increment = 1

        for ii in range(0, len(average_index_rows)-1):
                current_average_pixel = average_index_rows[ii]

                for pixel in range(-1, 1):
                    if (current_average_pixel + pixel > -100) and (current_average_pixel + pixel < 100):
                        (x_translated, y_translated) = ImageAnalyser.ConvertToImageCoOrds((current_average_pixel + pixel), y_indices[ii], (self._width/2, self._height/2), self._scan_direction)
                        img_pixels[x_translated, y_translated] = (255, 10, 10)

        # resize so the result can be seen

        image = self._debugimage.resize((500, 500))
        image.show()


class InterpolateAverages:
    """This class takes the average row/columns and approximates them with lines
    ready to add to the path"""

    def __init__(self, average_indices):

        self._average_indices = average_indices



    def ApproximateWithLine(start_point, x_indices, y_indices):
        """
        Approximates gradient of line assuming that the line goes through the start point

        Gives gradient y = mx
        """


        x_translated = x_indices  - start_point[0]

        y_translated = y_indices - start_point[1]
        x_translated = x_translated[:, np.newaxis]
        a, _, _, _ = np.linalg.lstsq(x_translated, y_translated)

        c = start_point[1] - start_point[0]*a[0]
        return a[0], c


    def ErrorFromLine(line, x_indices, y_indices, max_error):
        """
        Error from line y = mx + c, where line =(m, c) in the inputs.
        This functions fins the first index along the line where the error is greater than the max error bound.
        """

        line_normal = np.array([1, -1/line[0]])
        line_normal = line_normal/math.sqrt(1+1/(line[0] * line[0]))

        origin = np.asarray([0, line[1]])



        for index in range(0, len(x_indices)):

            indices = np.asarray([x_indices[index], y_indices[index]])
            error = InterpolateAverages.Error(line_normal, origin, indices)

            if error > max_error:
                return index




        return -1



    def Error(line_normal, line_origin, indices):

        if indices[0] != -1:
            error = abs(np.dot(line_normal, indices - line_origin))
        else:
            error = 0.0

        return error

