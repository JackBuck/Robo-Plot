import unittest
import matplotlib.pyplot as plt
import numpy as np
import ImageProcessing as IP
import time
from PIL import Image
from PIL import ImageDraw

#Each set of tests can be in their own class, but it much deriv from unnit.TestCase
class ImageTest(unittest.TestCase):

    #Each test has its own function here. There are lots of different functions to use in tests see
    def testPass(self):
        self.failUnless(True)

    def testCentroid(self):

        lightnesses = np.array([0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0])
        centroid = IP.ImageAnalyser.compute_weighted_centroid(lightnesses)
        self.failUnlessEqual(centroid, 8)

        lightnesses = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        centroid = IP.ImageAnalyser.compute_weighted_centroid(lightnesses)
        self.failUnlessEqual(centroid, -1)

        lightnesses = np.array([IP.white_threshold, IP.white_threshold, IP.white_threshold, IP.white_threshold, IP.white_threshold, IP.white_threshold-1, IP.white_threshold-1, IP.white_threshold-1, IP.white_threshold-1, IP.white_threshold-1, IP.white_threshold-1,
                                IP.white_threshold - 1, IP.white_threshold-1, IP.white_threshold+1, IP.white_threshold+1, IP.white_threshold+1, IP.white_threshold+1, IP.white_threshold+1])
        centroid = IP.ImageAnalyser.compute_weighted_centroid(lightnesses)
        self.failUnlessEqual(centroid, 15)

        lightnesses = np.array([255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0])
        centroid = IP.ImageAnalyser.compute_weighted_centroid(lightnesses)
        self.failUnlessEqual(centroid, 8)


    def testApproximateWithLine(self):
        x_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        y_indices = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        m = IP.InterpolateAverages.ApproximateWithLine(x_indices, y_indices)
        np.testing.assert_almost_equal(m, 0)

        x_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        y_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        m = IP.InterpolateAverages.ApproximateWithLine(x_indices, y_indices)
        np.testing.assert_almost_equal(m, 1)

        x_indices = np.array([0, 1, 3, 3, 2, 5, 6, 8, 8, 9, 10, 11])
        y_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        m = IP.InterpolateAverages.ApproximateWithLine(x_indices, y_indices)
        np.testing.assert_almost_equal(m, 1.0019763)

        x_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        y_indices = np.array([2, 1, 1, 3, 3, 5, 6, 7, 7, 9, 10, 10])
        m = IP.InterpolateAverages.ApproximateWithLine(x_indices, y_indices)
        np.testing.assert_almost_equal(m, 1.36328125)



    def testErrorFromLine(self):

        x_indices = np.array([0, 1, 3, 3, 2, 5, 6, 8, 8, 9, 10, 11])
        y_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        error = IP.InterpolateAverages.ErrorFromLine((1.0019763, 0.0), x_indices, y_indices)
        np.testing.assert_almost_equal(error[0], 1.4184010980)
        self.failUnlessEqual(error[1], 4)


        x_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        y_indices = np.array([2, 1, 1, 3, 3, 5, 6, 7, 7, 9, 10, 10])
        error = IP.InterpolateAverages.ErrorFromLine((1.3717949, 0.0), x_indices, y_indices)
        np.testing.assert_almost_equal(error[0],  2.190130073)
        self.failUnlessEqual(error[1], 10)


    def testConvertToImageCoOrds(self):

        #Test conversion with +x +y diagonal.
        x_indices = np.arange(100)
        y_indices = np.arange(100)
        centre = (100, 100)

        #North
        scan_direction = IP.Direction.North
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 200))
        np.testing.assert_equal(y_translated, np.arange(100, 0, -1))

        #East
        scan_direction = IP.Direction.East
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 200))
        np.testing.assert_equal(y_translated, np.arange(100, 200))

        #South
        scan_direction = IP.Direction.South
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 0, -1))
        np.testing.assert_equal(y_translated, np.arange(100, 200))

        #West
        scan_direction = IP.Direction.West
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 0, -1))
        np.testing.assert_equal(y_translated, np.arange(100, 0, -1))


        #Test -x +y
        x_indices = np.arange(0, -100, -1)

        # North
        scan_direction = IP.Direction.North
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 0, -1))
        np.testing.assert_equal(y_translated, np.arange(100, 0, -1))

        # East
        scan_direction = IP.Direction.East
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 200))
        np.testing.assert_equal(y_translated, np.arange(100, 0, -1))

        # South
        scan_direction = IP.Direction.South
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 200))
        np.testing.assert_equal(y_translated, np.arange(100, 200))

        # West
        scan_direction = IP.Direction.West
        (x_translated, y_translated) = IP.ImageAnalyser.ConvertToImageCoOrds(x_indices, y_indices, centre, scan_direction)
        #TestUtils.ShowPoints(x_translated, y_translated)
        np.testing.assert_equal(x_translated, np.arange(100, 0, -1))
        np.testing.assert_equal(y_translated, np.arange(100, 200))



class TestUtils:
    def ShowPoints(x_indices, y_indices):

        image = Image.new("RGB", (200, 200), (255, 255, 255))

        for i in range(0, len(x_indices)):
            if (x_indices[i] == -1):
                continue

            x_coord = x_indices[i]
            y_coord = y_indices[i]

            draw = ImageDraw.Draw(image)
            draw.ellipse((x_coord -1, y_coord - 1, x_coord + 1, y_coord + 1), fill = 'blue', outline='blue')
            del draw

        image.show()