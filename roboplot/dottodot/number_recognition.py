import glob
import PIL.Image as Image
import os
import re
import threading
import warnings

import cv2
import numpy as np
import pytesseract

import roboplot.config as config
import roboplot.dottodot.contour_tools as contour_tools
import roboplot.dottodot.misc as misc


class LocalNumber:
    """Represents a number on a photo taken of a local area on the dot-to-dot."""

    def __init__(self, numeric_value: int, dot_location_yx_pixels, recognised_text: str=None):
        """
        Create an instance to represent a number on the dot-to-dot picture.
        
        Args:
            numeric_value (int): the ordinal associated with the dot-to-dot number
            dot_location_yx_pixels: a pair (y,x) of floats specifying the location of the dot in the photo
        """
        self.numeric_value = numeric_value
        self.dot_location_yx_pixels = np.array(dot_location_yx_pixels)
        self.recognised_text = recognised_text


class GlobalNumber:
    """Represents a number in the global dot-to-dot context."""

    @staticmethod
    def from_local(local_number: LocalNumber, camera_location):
        global_location = misc.convert_image_point_to_global_coordinates(local_number.dot_location_yx_pixels,
                                                                         camera_location)
        return GlobalNumber(local_number.numeric_value, global_location, local_number.recognised_text)

    def __init__(self, numeric_value: int, dot_location_yx_mm, recognised_text: str = None):
        """
        Create an instance to represent a number on the dot-to-dot picture.

        Args:
            numeric_value (int): the ordinal associated with the dot-to-dot number
            dot_location_yx_mm: a pair (y,x) of floats specifying the location (in mm) of the dot on the page
        """
        self.numeric_value = numeric_value
        self.dot_location_yx_mm = np.array(dot_location_yx_mm)
        self.recognised_text = recognised_text


class NamedImage:
    def __init__(self, image: np.ndarray, name: str):
        self.image = image
        self.name = name


class DotToDotImage:
    """A class to process dot-to-dot images."""

    # This value for the _min_pixels_between_contour_groups 'only just' works for 40pt.
    # Unfortunately the spot size doesn't really grow in proportion to the font size - to do it dynamically we
    # would need to actually look at distances between contours and choose a threshold based on that, maybe using
    # some sort of clustering algorithm.
    _min_pixels_between_contour_groups = 10

    @staticmethod
    def load_image_from_file(file_path: str) -> 'DotToDotImage':
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

    def process_image(self) -> None:
        """
        Process the dot-to-dot image.

        Returns:
            LocalNumber: the number whose spot is closest to the centre of the image
        """
        self.intermediate_images = [self.intermediate_images[0]]  # Just keep the original image
        self._clean_image()
        self._extract_contour_groups()
        self._mask_to_remove_contour_groups_near_edge()
        self._extract_spots()
        self._recognise_number_near_each_spot()

    def _clean_image(self) -> None:
        self._img = cv2.medianBlur(self._img, ksize=3)
        self._img = cv2.adaptiveThreshold(self._img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Clean Image'))

    def _extract_contour_groups(self) -> None:
        contours = contour_tools.extract_black_contours(self._img)
        self._log_contours_on_current_image(contours, 'Contours')
        self.contour_groups = contour_tools.group_contours(contours, self._min_pixels_between_contour_groups)

    def _mask_to_remove_contour_groups_near_edge(self) -> None:
        contours_near_edge = []  # type: list[np.ndarray]
        for i in reversed(range(len(self.contour_groups))):
            if self._contour_group_is_near_edge(self.contour_groups[i]):
                contours_near_edge.extend(
                    self.contour_groups.pop(i))

        self._log_contours_on_current_image(contours_near_edge, 'Contours near edge')
        self._img = contour_tools.mask_using_contour_groups(self._img, self.contour_groups)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Contours near edge removed'))

    def _contour_group_is_near_edge(self, contour_group) -> bool:
        """
        Args:
            contour_group (list[np.ndarray]):
        """
        # A contour is an nx2 numpy array of (x,y) points
        min_xy = [self._min_pixels_between_contour_groups, self._min_pixels_between_contour_groups]
        max_xy = np.array([self._img.shape[1], self._img.shape[1]]) - self._min_pixels_between_contour_groups

        contour_is_near_edge = [np.any(contour < min_xy) or np.any(contour >= max_xy) for contour in contour_group]
        return any(contour_is_near_edge)

    def _extract_spots(self) -> None:
        # Dilate and Erode to 'clean' the spot (nb that this harms the number itself, so we only do it to extract spots)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img = cv2.dilate(self._img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=2)
        img = cv2.dilate(img, kernel, iterations=1)

        # Perform a simple blob detect
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 20  # The dot in 20pt font has area of about 30
        params.filterByCircularity = True
        params.minCircularity = 0.7
        params.filterByConvexity = True
        params.minConvexity = 0.8
        params.filterByInertia = True
        params.minInertiaRatio = 0.4
        detector = cv2.SimpleBlobDetector_create(params)
        self.spot_keypoints = detector.detect(img)

        # Log intermediate image
        img_with_keypoints = cv2.drawKeypoints(img, self.spot_keypoints, outImage=np.array([]), color=(0, 0, 255),
                                               flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self.intermediate_images.append(NamedImage(img_with_keypoints, 'Spot Detection Image'))

    def _recognise_number_near_each_spot(self) -> None:
        self.recognised_numbers = []  # type: list[LocalNumber]
        original_image = self._img
        for spot in self.spot_keypoints:
            self._img = original_image
            self._mask_to_contour_groups_close_to(spot.pt, self._min_pixels_between_contour_groups)
            self._rotate_keypoint_to_bottom_right(spot)
            number, text = self._recognise_number()

            self.recognised_numbers.append(
                LocalNumber(numeric_value=number,
                            dot_location_yx_pixels=(spot.pt[1], spot.pt[0]),
                            recognised_text=text)
            )

    def _mask_to_contour_groups_close_to(self, point_xy, delta: float) -> None:
        nearby_contour_groups = contour_tools.extract_contour_groups_close_to(self.contour_groups, point_xy, delta)
        self._img = contour_tools.mask_using_contour_groups(self._img, nearby_contour_groups)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Neighbourhood of Keypoint'))

    def _rotate_keypoint_to_bottom_right(self, keypoint: cv2.KeyPoint) -> None:
        current_degrees = self._estimate_current_anticlockwise_degrees(keypoint)
        self._img = _rotate_image_anticlockwise_without_cropping(-current_degrees, self._img)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Rotated Image'))

    def _estimate_current_anticlockwise_degrees(self, keypoint):
        # We use two methods of estimating the  angle.
        # For most numbers, righting the minimum-area-rectangle suffices.
        # However, for the number 4 it is skewed.
        # Hence, we compare it with the estimate from using the angle from the spot to the centroid, and if they
        # differ too much, rotate it using the centroid (because it is likely we have the number 4!)
        degrees_minarearect = self._estimate_current_anticlockwise_degrees_using_minarearect(spot_xy=keypoint.pt)
        degrees_centroid = self._estimate_current_anticlockwise_degrees_using_centroid(spot_xy=keypoint.pt)

        if abs(degrees_centroid - degrees_minarearect) < 15:
            return degrees_minarearect
        else:
            return degrees_centroid

    def _estimate_current_anticlockwise_degrees_using_minarearect(self, spot_xy) -> float:
        # Find the minimum area rectangle around the number
        nearby_contour_groups = contour_tools.extract_contour_groups_close_to(
            self.contour_groups, target_point_xy=spot_xy, delta=self._min_pixels_between_contour_groups)
        nearby_contours = [c for grp in nearby_contour_groups for c in grp]
        box = cv2.minAreaRect(np.row_stack(nearby_contours))
        corners_xy = cv2.boxPoints(box).astype(np.int32)
        self._log_contours_on_current_image([corners_xy], name="Minimum area rectangle")

        # Construct a vector which, once correctly rotated, goes from the bottom right corner up & left at 135 degrees
        sorted_corners = sorted(corners_xy, key=lambda pt: np.linalg.norm(spot_xy - pt))
        bottom_right_corner = sorted_corners[0]  # The closest corner to the spot
        adjacent_corners = sorted_corners[1:3]  # The next two closest corners

        unit_vectors_along_box_edge = misc.normalised(adjacent_corners - bottom_right_corner)
        up_left_diagonal = unit_vectors_along_box_edge.sum(axis=0)

        degrees_of_up_left_diagonal = np.rad2deg(np.arctan2(-up_left_diagonal[1], up_left_diagonal[0]))
        return degrees_of_up_left_diagonal - 135

    def _estimate_current_anticlockwise_degrees_using_centroid(self, spot_xy) -> float:
        inverted_image = _invert(self._img)

        total_intensity = np.sum(inverted_image)
        centroid_y = np.sum(
            np.arange(inverted_image.shape[0]).reshape(-1, 1) * inverted_image) / total_intensity
        centroid_x = np.sum(
            np.arange(inverted_image.shape[1]).reshape(1, -1) * inverted_image) / total_intensity

        x = spot_xy[0]
        y = spot_xy[1]
        # The subtracted number fails with number 4 for both 150 and 147. But 148.5 also fails!
        return np.rad2deg(np.arctan2(-(centroid_y - y), centroid_x - x)) - 149

    def _log_contours_on_current_image(self, contours, name: str) -> None:
        """
        Args:
            contours (list[np,ndarray]):
        """
        img = cv2.cvtColor(self._img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img, contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
        self.intermediate_images.append(NamedImage(img, name))

    def _recognise_number(self) -> (int, str):
        text = self._recognise_number_text()
        return self._extract_number_from_recognised_text(text), text

    def _recognise_number_text(self) -> str:
        img = Image.fromarray(self._img)

        # psm 8 => single word;
        # digits => use the digits config file supplied with the software
        return pytesseract.image_to_string(img, config='-psm 8, digits')

    @staticmethod
    def _extract_number_from_recognised_text(recognised_text: str) -> int:
        # Forcing a terminating period helps us to filter out bad results
        # Allowing an initial period is a (small) hack to make one of the tests pass (the test recognises '.17.' due
        # to a small amount of noise in the photo next to the 1). Ideally this would be done through image processing.
        match = re.match(r'(\.)?(\d+)\.$', recognised_text)

        if match is not None:
            if match.group(1) is not None:
                warnings.warn('Matched partially non-conforming text: {}'.format(recognised_text))

            return int(match.group(2))

    def display_intermediate_images(self) -> None:
        for img in self.intermediate_images:
            cv2.imshow(winname=img.name, mat=img.image)
            cv2.waitKey(0)

    _default_intermediate_image_save_path_prefix = os.path.join(config.debug_output_folder, 'numrec_')

    @staticmethod
    def delete_intermediate_image_files(save_path_prefix: str = _default_intermediate_image_save_path_prefix) -> None:
        for f in glob.glob(save_path_prefix + '*.jpg'):
            os.remove(f)

    def save_intermediate_images(self, save_path_prefix: str = _default_intermediate_image_save_path_prefix) -> None:
        counter = -1
        for img in self.intermediate_images:
            counter += 1

            save_dir = os.path.dirname(save_path_prefix)

            save_name = os.path.basename(save_path_prefix + str(counter) + '_' + img.name)
            save_name = re.sub(r'\s+', '_', save_name)  # Replace whitespace with underscores
            save_name = re.sub(r'[^\w\s-]', '', save_name)  # Remove all weird characters
            save_name += '.jpg'

            save_path = os.path.join(save_dir, save_name)

            image = img.image.copy()
            threading.Thread(target=lambda: cv2.imwrite(save_path, image)).start()

    def print_recognised_local_numbers(self) -> None:
        print("Recognised {} numbers:".format(len(self.recognised_numbers)))
        for number in self.recognised_numbers:
            print("  * ", end='')
            if number.numeric_value is not None:
                print("{:2d}".format(number.numeric_value), end='')
            else:
                print("??", end='')
            if number.recognised_text is not None:
                print(" ({!r})".format(number.recognised_text), end='')
            print(": ({0[0]:.1f}, {0[1]:.1f})".format(number.dot_location_yx_pixels))
        print('')


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


def _rotate_image_anticlockwise_without_cropping(degrees: float, img: np.ndarray) -> np.ndarray:
    # Adapted from:
    # http://stackoverflow.com/questions/22041699/rotate-an-image-without-cropping-in-opencv-in-c/33564950#33564950

    # Extract dimensions etc.
    height, width = img.shape[:2]
    image_center = (width / 2, height / 2)

    # Get the usual rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(image_center, degrees, 1.)

    # Compute the new desired dimensions
    abs_cos = abs(np.cos(np.deg2rad(degrees)))
    abs_sin = abs(np.sin(np.deg2rad(degrees)))

    new_width = int(np.ceil(width * abs_cos + height * abs_sin))
    new_height = int(np.ceil(height * abs_cos + width * abs_sin))

    # Add a translation to the rotation matrix
    rotation_matrix[0, 2] += new_width / 2 - image_center[0]
    rotation_matrix[1, 2] += new_height / 2 - image_center[1]

    # Rotate the image, and ask opencv to return the larger canvas
    rotated_image = cv2.warpAffine(img, rotation_matrix, (new_width, new_height),
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=255)

    return rotated_image


def _crop_about(img, centre: (int, int), new_side_length: float) -> (int, int):
    new_side_length = 2 * int(new_side_length / 2)

    cropped_img = img[
                  max(0, centre[0] - new_side_length / 2): centre[0] + new_side_length / 2 + 1,
                  max(0, centre[1] - new_side_length / 2): centre[1] + new_side_length / 2 + 1]

    new_centre = (min(centre[0], new_side_length / 2),
                  min(centre[1], new_side_length / 2))

    return cropped_img, new_centre


def _invert(img: np.ndarray) -> np.ndarray:
    return 255 - img


def draw_image_with_keypoints(img: np.ndarray, keypoints, window_title: str ="Image with keypoints") -> None:
    """An apparently unused method which is actually quite useful when debugging!"""

    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, outImage=np.array([]), color=(0, 0, 255),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    draw_image(img_with_keypoints, window_title)


def draw_image_with_contours(img: np.ndarray, contours, window_title: str = "Image with contours") -> None:
    img_colour = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(img_colour, contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
    draw_image(img_colour, window_title)


def draw_image(img: np.ndarray, window_title: str = "Image") -> None:
    cv2.imshow(window_title, img)
    cv2.waitKey(0)


def print_recognised_global_numbers(global_numbers) -> None:
    """
    Args:
        global_numbers (list[GlobalNumber]):
    """
    print("Recognised {} numbers:".format(len(global_numbers)))
    for number in global_numbers:
        print("  * ", end='')
        if number.numeric_value is not None:
            print("{:2d}".format(number.numeric_value), end='')
        else:
            print("??", end='')
        if number.recognised_text is not None:
            print(" ({!r})".format(number.recognised_text), end='')
        print(": ({0[0]:.1f}, {0[1]:.1f})".format(number.dot_location_yx_mm))
    print('')


def print_recognised_global_numbers_to_string(global_numbers) -> list:
    output = ["Recognised {} numbers:".format(len(global_numbers))]
    for number in global_numbers:
        if number.numeric_value is not None:
            recognised_number = "{:2d}".format(number.numeric_value)
        else:
            recognised_number = "??"
        if number.recognised_text is not None:
            recognised_text = " ({!r})".format(number.recognised_text)
        else:
            recognised_text = ""
        output.append("  * {0}{1}: ({2[0]:.1f}, {2[1]:.1f})".format(recognised_number, recognised_text,
                                                                  number.dot_location_yx_mm))
    output.append("")
    return output
