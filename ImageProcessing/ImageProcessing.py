from enum import Enum
from PIL import Image
import numpy as np

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
        x = np.arange(num_elements[0])
        is_white = lightnesses > 130
        num_white = sum(is_white)
        weighted = np.multiply(is_white, x)
        np.savetxt('weight.txt', weighted)
        if num_white == 0:
            return -1
        else:
            flt_centroid = sum(is_white * x) / num_white

        if flt_centroid == 0.0:
            return -1
        else:
            return int(flt_centroid)

    def AnalyseImage(self, scan_direction):

    #Get average pixel positions.
        if(scan_direction == Direction.North):
            average_pixels = self.AnalyseRow(True)
        elif(scan_direction == Direction.East):
            average_pixels = self.AnalyseCol(True)
        elif (scan_direction == Direction.South):
            average_pixels = self.AnalyseRow(False)
        elif (scan_direction == Direction.West):
            average_pixels = self.AnalyseCol(False)


        #Calculate the average index in the direction required.

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
            min_index = max(0, average_index_rows[count]-self._tol)
            max_index = min(self._height, average_index_rows[count]+self._tol)
            count += 1
            sub_array = self._pixels[ rr, min_index:max_index]
            next_centroid = ImageAnalyser.compute_weighted_centroid((sub_array))
            average_index_rows.append(next_centroid)
        if (debug):
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
            min_index = max(0, average_index_cols[count] - self._tol)
            max_index = min(self._height, average_index_cols[count] + self._tol)
            count += 1
            sub_array = self._pixels[min_index:max_index, cc]
            next_centroid = ImageAnalyser.compute_weighted_centroid((sub_array))
            average_index_cols.append(next_centroid)


        if(debug):
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
        self._img = self._img.resize((2000, 2000))
        self._img.show()

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
        self._img = self._img.resize((2000, 2000))
        self._img.show()