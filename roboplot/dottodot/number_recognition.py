import PIL.Image as Image
import re

import cv2
import numpy as np
import pytesseract


class Number:
    """Represents a number on the dot-to-dot picture."""

    def __init__(self, numeric_value: int, dot_location_yx: tuple):
        """
        Create an instance to represent a number on the dot-to-dot picture.
        
        Args:
            numeric_value (int): the ordinal associated with the dot-to-dot number\n
            dot_location_yx (tuple): a pair (y,x) of floats specifying the location of the dot in the photo
        """
        self.numeric_value = numeric_value
        self.dot_location_yx = dot_location_yx


class NamedImage:
    def __init__(self, image, name):
        self.image = image
        self.name = name


class DotToDotImage:
    """A class to process dot-to-dot images."""

    @staticmethod
    def load_image_from_file(file_path: str):
        """
        Load an image from a supplied file path.

        Args:
            file_path (str): path to the image to return

        Returns:
            DotToDotImage: the loaded (unprocessed) image
        """
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            return DotToDotImage(img)
        else:
            raise TypeError("Could not open image file: {}".format(file_path))

    def __init__(self, original_img):
        """
        Create an unprocessed dot-to-dot image.

        Args:
            original_img (np.ndarray): the image to proccess
        """
        self._img = original_img
        self.intermediate_images = [NamedImage(self._img.copy(), 'Original Image')]

    def process_image(self) -> Number:
        """
        Process the dot-to-dot image.

        Returns:
            Number: the number whose spot is closest to the centre of the image
        """
        self.intermediate_images = [self.intermediate_images[0]]  # Just keep the original image
        self._clean_image()
        self._extract_spots()
        self._find_closest_spot_to_centre()
        self._extract_central_contours(maximum_pixels_between_contours=9)
        self._mask_using_central_contours()
        self._rotate_centre_spot_to_bottom_right()
        self._recognise_number_text()
        self._extract_number_from_recognised_text()
        return Number(numeric_value=self.recognised_numeric_value,
                      dot_location_yx=(self.centre_spot.pt[1], self.centre_spot.pt[0]))

    def _clean_image(self):
        self._img = cv2.medianBlur(self._img, ksize=3)
        self._img = cv2.adaptiveThreshold(self._img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Clean Image'))

    def _extract_spots(self):
        # Dilate and Erode to 'clean' the spot (note that this harms the number itself, so we only do it to extract spots
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img = cv2.dilate(self._img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        # Perform a simple blob detect
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 20  # The dot in 20pt font has area of about 30
        params.filterByCircularity = True
        params.minCircularity = 0.7
        params.filterByConvexity = True
        params.minConvexity = 0.8
        params.filterByInertia = True
        params.minInertiaRatio = 0.6
        detector = cv2.SimpleBlobDetector_create(params)
        self.spot_keypoints = detector.detect(img)

        # Log intermediate image
        img_with_keypoints = cv2.drawKeypoints(img, self.spot_keypoints, outImage=np.array([]), color=(0, 0, 255),
                                               flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self.intermediate_images.append(NamedImage(img_with_keypoints, 'Spot Detection Image'))

    def _find_closest_spot_to_centre(self):
        if self.spot_keypoints is None or len(self.spot_keypoints) == 0:
            self.centre_spot = None
        else:
            image_centre = np.array(self._img.shape) / 2
            self.centre_spot = min(self.spot_keypoints, key=lambda s: np.linalg.norm(s.pt - image_centre))

            try:
                spots_image = next(img.image for img in self.intermediate_images if img.name == 'Spot Detection Image')
                cv2.circle(spots_image, tuple(int(i) for i in self.centre_spot.pt), radius=int(self.centre_spot.size),
                           color=(0, 255, 0), thickness=2)
            except StopIteration:
                pass

    def _extract_central_contours(self, maximum_pixels_between_contours: float):
        self.central_contours = None
        if self.centre_spot is not None:
            self.central_contours = self._extract_contours_close_to(self.centre_spot.pt,
                                                                    maximum_pixels_between_contours)

            # Log intermediate image
            img = cv2.cvtColor(self._img.copy(), cv2.COLOR_GRAY2BGR)
            cv2.drawContours(img, self.central_contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
            self.intermediate_images.append(NamedImage(img, 'Central contours'))

    def _extract_contours_close_to(self, target_point, maximum_pixels_between_contours: float):
        img_inverted = 255 - self._img
        _, all_contours, _ = cv2.findContours(img_inverted, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

        def dist_between_contours(cnt1, cnt2):
            return min([min(np.linalg.norm(cnt1 - pt, axis=2)) for pt in cnt2])

        # all_contours = [cv2.convexHull(c, returnPoints=True) for c in all_contours]

        target_point_as_contour = np.reshape(target_point, (-1, 1, 2))
        contours_near_target = [target_point_as_contour]

        still_adding_contours = True
        while still_adding_contours:
            still_adding_contours = False

            for i in reversed(range(len(all_contours))):
                dist_from_central_contours = min(
                    [dist_between_contours(all_contours[i], c) for c in contours_near_target])
                if dist_from_central_contours <= maximum_pixels_between_contours:
                    contours_near_target.append(all_contours.pop(i))
                    still_adding_contours = True

        return contours_near_target[1:]

    def _mask_using_central_contours(self):
        if self.central_contours is not None:
            self._img = self._mask_using_contours(self.central_contours)
            self.intermediate_images.append(NamedImage(self._img.copy(), 'Masked Image'))

    def _mask_using_contours(self, contours):
        img = self._img.copy()
        mask = np.zeros(img.shape, np.uint8)
        cv2.drawContours(mask, contours, contourIdx=-1, color=255, thickness=-1)
        img[np.where(mask == 0)] = 255
        return img

    def _rotate_centre_spot_to_bottom_right(self):
        if self.centre_spot is not None:
            current_angle = self._estimate_degrees_from_number_centre_to_spot()
            desired_angle = -30
            self._img = _rotate_image_anticlockwise(desired_angle - current_angle, self._img)
            self.intermediate_images.append(NamedImage(self._img.copy(), 'Rotated Image'))

    def _estimate_degrees_from_number_centre_to_spot(self):
        inverted_image = 255 - self._img

        total_intensity = np.sum(inverted_image)
        centroid_y = np.sum(
            np.arange(inverted_image.shape[0]).reshape(-1, 1) * inverted_image) / total_intensity
        centroid_x = np.sum(
            np.arange(inverted_image.shape[1]).reshape(1, -1) * inverted_image) / total_intensity

        return np.rad2deg(np.arctan2(-(self.centre_spot.pt[1] - centroid_y),
                                     self.centre_spot.pt[0] - centroid_x))

    def _recognise_number_text(self):
        img = Image.fromarray(self._img)

        # psm 8 => single word;
        # digits => use the digits config file supplied with the software
        self.recognised_text = pytesseract.image_to_string(img, config='-psm 8, digits')

    def _extract_number_from_recognised_text(self):
        # Forcing a terminating period helps us to filter out bad results
        match = re.match(r'(\d+)\.$', self.recognised_text)
        self.recognised_numeric_value = None
        if match is not None:
            self.recognised_numeric_value = int(match.group(1))

    def display_intermediate_images(self):
        for img in self.intermediate_images:
            cv2.imshow(winname=img.name, mat=img.image)
            cv2.waitKey(0)


def read_image(file_path: str) -> np.ndarray:
    """
    Load an image from a supplied file path.

    Args:
        file_path (str): path to the image to return

    Returns:
        np.ndarray: the loaded image
    """
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        return img
    else:
        raise TypeError("Could not open image file: {}".format(file_path))


def _rotate_image_anticlockwise(degrees, img):
    rows, cols = img.shape
    rotation_matrix = cv2.getRotationMatrix2D(center=(cols / 2, rows / 2), angle=degrees, scale=1)
    rotated_image = cv2.warpAffine(img, rotation_matrix, (cols, rows))
    rotated_radians_mod_half_pi = np.deg2rad(degrees % 90)
    new_img_width = img.shape[0] / (np.cos(rotated_radians_mod_half_pi) + np.sin(rotated_radians_mod_half_pi))
    # Crop out the thin remaining border...
    new_img_width = 2 * int((img.shape[0] + new_img_width) / 2 - 1) - img.shape[0]
    rows, cols = rotated_image.shape
    rotated_image, _ = _crop_about(rotated_image, centre=(cols / 2, rows / 2), new_side_length=new_img_width)
    return rotated_image


def _crop_about(img, centre, new_side_length):
    new_side_length = 2 * int(new_side_length / 2)

    cropped_img = img[
                  max(0, centre[0] - new_side_length / 2): centre[0] + new_side_length / 2 + 1,
                  max(0, centre[1] - new_side_length / 2): centre[1] + new_side_length / 2 + 1]

    new_centre = (min(centre[0], new_side_length / 2),
                  min(centre[1], new_side_length / 2))

    return cropped_img, new_centre


def draw_image_with_keypoints(img, keypoints, window_title="Image with keypoints"):
    """An apparently unused method which is actually quite useful when debugging!"""

    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, outImage=np.array([]), color=(0, 0, 255),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    draw_image(img_with_keypoints, window_title)


def draw_image_with_contours(img, contours, window_title="Image with contours"):
    img_colour = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(img_colour, contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
    draw_image(img_colour, window_title)


def draw_image(img, window_title="Image"):
    cv2.imshow(window_title, img)
    cv2.waitKey(0)
