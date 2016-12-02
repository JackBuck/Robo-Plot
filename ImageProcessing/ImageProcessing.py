from enum import Enum
from PIL import Image
from PIL import ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import math

debug = True

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




class ImageAnalyser:
    """This class is holds the information to analyse the path."""

    def __init__(self, file_path):

        """

        Initialises the Image Analyser Class.

        Args:

            file_location: The location of the file to be analysed.

        """

        self._img = Image.open(file_path)

        # Currently resize the image this may be taken out if the photos are taken small enough
        # The actual size of the converted function may also be modified.

        self._width = 200
        self._height = 200
        self._img = self._img.resize((self._width, self._height))

        # Convert image to black and white - we cannot take the photos in black and white as we
        # must first search for the red triangle.
        self._img = self._img.convert('L')

        # Put pixels into an array for processing
        self._pixels = np.asarray(self._img)

        # Currently a simple tolerance is used based on the size of the image - this is assuming a
        # rough view of 50 x 50 mm^2.
        self._tol = min((self._width / 1.5), (self._height / 1.5))


    def compute_weighted_centroid(lightnesses):
        num_elements = lightnesses.shape
        np.savetxt('Lightnesses.txt', lightnesses, fmt="%2.1f", delimiter=',')

        x = np.arange(num_elements[0])
        is_white = lightnesses > 130
        num_white = sum(is_white)
        weighted = np.multiply(is_white, x)
        np.savetxt('weight.txt', weighted, fmt="%2.1f", delimiter=" , ")

        if num_white == 0:
            return -1
        else:
            flt_centroid = sum(is_white * x) / num_white

        return int(flt_centroid)


    #def compute_weighted_centroid(lightnesses):
    #    num_elements = lightnesses.shape[0]
    #    x = np.arange(num_elements)
#
    #    lightnesses = lightnesses/np.mean(lightnesses)
#
    #    centroid = np.mean(lightnesses * x)
#
    #    return centroid

    def AnalyseImage(self, scan_direction):

    #Get average pixel positions.


        if(scan_direction == Direction.North):
            average_pixels = np.array(self.AnalyseRow(False))
        elif(scan_direction == Direction.East):
            average_pixels = np.array(self.AnalyseCol(True))
        elif (scan_direction == Direction.South):
            average_pixels = np.array(self.AnalyseRow(True))
        elif (scan_direction == Direction.West):
            average_pixels = np.array(self.AnalyseCol(False))

        #Approximate the pixels with a line.

        a_interpolator = InterpolateAverages(average_pixels)

        if (scan_direction == Direction.North) or (scan_direction == Direction.South):
            x_indices = average_pixels
            y_indices = np.arange(len(x_indices))
        else:
            y_indices = average_pixels
            x_indices = np.arange(len(y_indices))



        max_error = 1e99
        segments = [0, len(x_indices)-1]
        lines = []
        segment_index = 0
        tol = 10

        while segments[segment_index] != len(x_indices)-1:
            while max_error > tol:
                start_index = segments[segment_index]
                end_index = segments[segment_index + 1]
                (m, c) = a_interpolator.ApproximateWithLine(x_indices[start_index: end_index], y_indices[start_index: end_index])


                lines.append((m,c))

                (max_error, index) = a_interpolator.ErrorFromLine((m, c), x_indices[start_index: end_index], y_indices[start_index: end_index])

                if max_error > tol:
                    segments.insert(segment_index + 1, index)

            segment_index += 1


        if(debug):

            self.ShowApproximation(lines, segments, x_indices, scan_direction)


    def ShowApproximation(self, lines, segments, x_indices, scan_direction):

        scale_factor_x = 2000/self._width
        scale_factor_y = 2000/self._height
        image = self._img.resize((2000, 2000))


        for current_line in range(0, len(lines)):
            (m, c) = lines[current_line]

            x_start_cart = x_indices[segments[current_line]]
            y_start_cart = (x_start_cart * m) + c
            (x_start_image, y_start_image) = self.ConvertToImageCoOrds(x_start_cart, y_start_cart, scan_direction, scale_factor_x, scale_factor_y)

            x_end_cart = x_indices[segments[current_line + 1]]
            y_end_cart = (x_end_cart * m) + c
            (x_end_image, y_end_image) = self.ConvertToImageCoOrds(x_end_cart, y_end_cart, scan_direction, scale_factor_x, scale_factor_y)

            #plt.plot((x_start_cart, x_end_cart), (y_start_cart, y_end_cart))
            #plt.show()

            draw = ImageDraw.Draw(image)


            draw.line([x_start_image, y_start_image, x_end_image, y_end_image], (50, 100, 240), 8)
            draw.ellipse((x_start_image - 8, y_start_image - 8, x_start_image + 8, y_start_image + 8), fill = 'blue', outline='blue')
            draw.ellipse((x_end_image - 8, y_end_image - 8, x_end_image + 8, y_end_image + 8), fill = 'blue', outline='blue')

            del draw

        image.show()



    def ConvertToImageCoOrds(self, x, y, scan_direction, scale_factor_x, scale_factor_y):
        if (scan_direction == Direction.North):
            x_image = x
            y_image = (self._height/2) - y
        elif (scan_direction == Direction.East):
            x_image = (self._width/2) + x
            y_image = y
        elif (scan_direction == Direction.South):
            x_image = self._width - x
            y_image = (self._height/2) - y
        elif (scan_direction == Direction.West):
            x_image = (self._width/2) - x
            y_image = self._height - y

        return (x_image*scale_factor_x, y_image*scale_factor_y)


    def AnalyseRow(self, is_pos):
        average_index_rows = []
        average_index_rows.append(int(self._width/2))

        if is_pos:
            increment = 1
            end_index = self._height
        else:
            increment = -1
            end_index = 0

        count = 0
        for rr in range(int(self._height/2), end_index, increment):
            min_index = int(max(0, average_index_rows[count]-self._tol))
            max_index = int(min(self._height, average_index_rows[count]+self._tol))

            count += 1
            sub_array = self._pixels[ rr, min_index:max_index]
            next_centroid = min_index + ImageAnalyser.compute_weighted_centroid(sub_array)
            average_index_rows.append(next_centroid)

        if debug:
            self.ShowDebugAverageRows(average_index_rows, is_pos)

            return average_index_rows


    def AnalyseCol(self, is_pos):

        average_index_cols = []
        average_index_cols.append(int(self._height / 2))

        if is_pos:
            increment = 1
            end_index = self._width
        else:
            increment = -1
            end_index = 0

        count = 0
        for cc in range(int(self._width / 2), end_index, increment):
            min_index = int(max(0, average_index_cols[count] - self._tol))
            max_index = int(min(self._height, average_index_cols[count] + self._tol))
            count += 1
            sub_array = self._pixels[min_index:max_index, cc]
            next_centroid = min_index + ImageAnalyser.compute_weighted_centroid(sub_array)
            average_index_cols.append(next_centroid)


        if debug:
            self.ShowDebugAverageCols(average_index_cols, is_pos)

            return average_index_cols


    def ShowDebugAverageRows(self, average_index_rows, is_pos):
        self._img = self._img.convert('RGB')
        img_pixel = self._img.load()
        
        if is_pos:
            increment = 1
        else:
            increment = -1

        row = int(self._height/2)

        for ii in range(1, len(average_index_rows)):
            if average_index_rows[ii] != -1:
                current_average_pixel = average_index_rows[ii]

                for pixel in range(-1, 1):
                    if (current_average_pixel + pixel > 0) and (current_average_pixel + pixel < self._height):
                        img_pixel[current_average_pixel + pixel, row] = (255, 10, 10)

            row += increment

        # resize so the result can be seen
        image = self._img.resize((2000, 2000))
        #image.show()


    def ShowDebugAverageCols(self, average_index_cols, is_pos):
        self._img = self._img.convert('RGB')
        img_pixel = self._img.load()

        if is_pos:
            increment = 1
        else:
            increment = -1

        col = int(self._width / 2)
        for ii in range(1, len(average_index_cols)):
            if average_index_cols[ii] != -1:
                current_average_pixel = average_index_cols[ii]

                for pixel in range(-1, 1):
                    if (current_average_pixel + pixel > 0) and (current_average_pixel + pixel < self._width):
                        img_pixel[col, current_average_pixel + pixel] = (10, 255, 10)
                        
            col += increment

        # resize so the result can be seen
        image = self._img.resize((2000, 2000))
        #image.show()



class InterpolateAverages:
    """This class takes the average row/columns and approximates them with lines
    ready to add to the path"""

    def __init__(self, average_indices):

        self._average_indices = average_indices



    def ApproximateWithLine(self, x_indices, y_indices):

         line = np.polyfit(x_indices, y_indices, 1)
         return line


    def ErrorFromLine(self, line, x_indices, y_indices):

        magnitude = math.sqrt(line[0] * line[0] + 1)
        line_normal = ((1/magnitude), -float(line[0])/magnitude)

        origin = np.asarray([0, line[1]])

        error=[]

        for index in range(0, len(x_indices)):

            indices = np.asarray([x_indices[index], y_indices[index]])
            error.append(InterpolateAverages.Error(line_normal, origin, indices))

        error_indices = np.argmax(error)

        return (error[error_indices], error_indices)



    def Error(line_normal, line_origin, indices):

        error = abs(np.dot(line_normal, indices - line_origin))

        return error

