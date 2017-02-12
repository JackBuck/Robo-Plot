# import the necessary packages
import numpy as np
import cv2


def detect_colour(hsv_image, hsv_boundary, min_size, change_to_white):
    """
    This function detects the largest feature in the image with pixels within the hsv boundary. If this
    feature is larger than the minimum size then the centre of this feature with respect to the centre
    of the image is returned.

    If change to white is set to true the original image is modified such that all pixels within the
    feature identified are now white.

    Args:
        hsv_image (numpy array):                The image to be analysed.
        hsv_boundary (tuple of lists length 3): The range of HSV colours to be detected. Note if the
                                                hue in the first list is larger than in the second it
                                                is assumed the interval should wrap around.
        min_size (int):                         The minimum number of pixels the largest feature must
                                                have to be "significant" enough to report.
        change_to_white (bool):                 Bool indicating whether the detected feature should be
                                                turned white

    Returns:
        tuple - co-ordinates of centre of the feature (wrt top left corner of image)

    """

    (lower, upper) = hsv_boundary

    # Convert boundaries to np arrays
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    # Create mask of pixels in range if the range spans both sides of 0 (red) then it will need to be considered as
    # two masks
    if lower[0] > upper[0]:
        lower_bound = lower[0]
        lower[0] = 0
        mask1 = cv2.inRange(hsv_image, lower, upper)
        lower[0] = lower_bound
        upper[0] = 180
        mask2 = cv2.inRange(hsv_image, lower, upper)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv_image, lower, upper)

    res = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)

    # find contours in the masked image
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    colour_found = False
    cnts = cnts[1]

    # loop over the contours - We should only have one significant region.
    for c in cnts:

        # if the contour is not sufficiently large, ignore it - #This number will need to depend on image size.
        size = cv2.contourArea(c)
        if cv2.contourArea(c) < min_size:
            continue

        colour_found = True
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            if __debug__:
                # draw the contour and center of the shape on the image
                image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
                cv2.drawContours(image, [c], -1, (255, 55, 255), int(image.shape[0]/80))
                cv2.circle(image, (cX, cY), 1, (255, 55, 255), int(image.shape[0]/80))
                image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                cv2.imwrite('../resources/Debug_Images/Colour_Detection.jpg', image)
            if change_to_white:
                hsv_image[mask == 255] = [0, 0, 255]

    if colour_found:
        return cX, cY
    else:
        return -1, -1


def detect_red(hsv_image, min_size, change_to_white):
    """
    This function detects the largest feature in the image with red pixels. If this
    feature is larger than the minimum size then the centre of this feature with respect to the centre
    of the image is returned.

    If change to white is set to true the original image is modified such that all pixels within the
    feature identified are now white.

    Args:
        hsv_image (numpy array):                The image to be analysed.
        min_size (int):                         The minimum number of pixels the largest feature must
                                                have to be "significant" enough to report.
        change_to_white (bool):                 Bool indicating whether the detected feature should be
                                                turned white

    Returns:
        tuple - co-ordinates of centre of the feature (wrt top left corner of image)

    """

    hsv_boundary = ([165, 100, 100], [10, 255, 255])

    (cX, cY) = detect_colour(hsv_image, hsv_boundary, min_size, change_to_white)

    return cX, cY


def detect_green(hsv_image, min_size, change_to_white):
    """
    This function detects the largest feature in the image with green pixels. If this
    feature is larger than the minimum size then the centre of this feature with respect to the centre
    of the image is returned.

    If change to white is set to true the original image is modified such that all pixels within the
    feature identified are now white.

    Args:
        hsv_image (numpy array):                The image to be analysed.
        min_size (int):                         The minimum number of pixels the largest feature must
                                                have to be "significant" enough to report.
        change_to_white (bool):                 Bool indicating whether the detected feature should be
                                                turned white

    Returns:
        tuple - co-ordinates of centre of the feature (wrt top left corner of image)

    """

    hsv_boundary = ([40, 50, 50], [80, 255, 255])

    (cX, cY) = detect_colour(hsv_image, hsv_boundary, min_size, change_to_white)

    return cX, cY





