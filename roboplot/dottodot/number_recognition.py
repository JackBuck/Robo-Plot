import glob
import PIL.Image as Image
import os
import re
import threading

import cv2
import numpy as np
import pytesseract

import roboplot.config as config


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

    # This value for the _max_pixels_between_contours_in_same_group 'only just' works for 40pt.
    # Unfortunately the spot size doesn't really grow in proportion to the font size - to do it dynamically we
    # would need to actually look at distances between contours and choose a threshold based on that, maybe using
    # some sort of clustering algorithm.
    _max_pixels_between_contours_in_same_group = 10

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

    def process_image(self) -> None:
        """
        Process the dot-to-dot image.

        Returns:
            Number: the number whose spot is closest to the centre of the image
        """
        self.intermediate_images = [self.intermediate_images[0]]  # Just keep the original image
        self._clean_image()
        self._extract_contour_groups()
        self._mask_to_remove_contour_groups_near_edge()
        self._extract_spots()
        self._recognise_number_near_each_spot()

    def _clean_image(self):
        self._img = cv2.medianBlur(self._img, ksize=3)
        self._img = cv2.adaptiveThreshold(self._img, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          thresholdType=cv2.THRESH_BINARY, blockSize=11, C=2)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Clean Image'))

    def _extract_contour_groups(self):
        contours = self._extract_contours()
        self.contour_groups = self._group_contours(contours)

    # TODO: Break out a contourtools module...

    def _extract_contours(self) -> list:
        img_inverted = 255 - self._img
        _, contours, _ = cv2.findContours(img_inverted, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        self._log_contours_on_current_image(contours, 'Contours')
        return contours

    def _group_contours(self, contours) -> list:
        """
        Group contours, returning a list of lists of contours.

        Args:
            contours [list[np.ndarray]]: a list of contours to group.

        Returns:
            list[list[np.ndarray]]: each element is a group of contours.

        """
        contour_groups = [[c] for c in contours]
        contour_distance_matrix = _compute_contour_distance_matrix(contours)

        inds_of_mergeable_pair = self._compute_indices_of_one_pair_of_mergeable_groups(contour_distance_matrix)
        while inds_of_mergeable_pair is not None:
            contour_groups, contour_distance_matrix = self._merge_contour_groups(contour_groups,
                                                                                 contour_distance_matrix,
                                                                                 inds_of_mergeable_pair)
            inds_of_mergeable_pair = self._compute_indices_of_one_pair_of_mergeable_groups(contour_distance_matrix)

        return contour_groups

    def _compute_indices_of_one_pair_of_mergeable_groups(self, contour_distance_matrix):
        # Get all indices (i,j) with i<j, in a 2-element tuple (all rows indices, all column indices).
        inds = np.triu_indices_from(contour_distance_matrix, 1)
        # Get a boolean vector which indexes both elements of inds and tells whether the pair of groups should be merged
        groups_should_be_merged = contour_distance_matrix[inds] < self._max_pixels_between_contours_in_same_group
        # Get the subset of indices for groups we can merge
        inds_of_mergeable_groups = [inds[i][groups_should_be_merged] for i in range(len(inds))]
        # Return the first pair of indices, if any were found
        indices_matrix = np.transpose(inds_of_mergeable_groups)
        return indices_matrix[0] if len(indices_matrix) > 0 else None

    @staticmethod
    def _merge_contour_groups(contour_groups, current_distance_matrix, inds_of_mergeable_pair):
        # Merge the actual contour groups
        new_contour_groups = contour_groups.copy()
        first_group = new_contour_groups.pop(max(inds_of_mergeable_pair))
        second_group = new_contour_groups.pop(min(inds_of_mergeable_pair))
        new_contour_groups.append(first_group + second_group)

        # Merge rows and columns in the distance matrix
        new_distances = current_distance_matrix[inds_of_mergeable_pair, :].min(axis=0)

        groups_to_keep = np.ones(len(current_distance_matrix), dtype=bool)
        groups_to_keep[inds_of_mergeable_pair] = False

        new_distance_matrix = np.zeros([i-1 for i in current_distance_matrix.shape])
        new_distance_matrix[0:-1, 0:-1] = current_distance_matrix[groups_to_keep,:][:, groups_to_keep]
        new_distance_matrix[-1, 0:-1] = new_distances[groups_to_keep]
        new_distance_matrix[0:-1, -1] = new_distances[groups_to_keep]

        return new_contour_groups, new_distance_matrix

    def _mask_to_remove_contour_groups_near_edge(self) -> None:
        contours_near_edge = []
        for i in reversed(range(len(self.contour_groups))):
            if self._contour_group_is_near_edge(self.contour_groups[i]):
                contours_near_edge.extend(
                    self.contour_groups.pop(i))

        self._log_contours_on_current_image(contours_near_edge, 'Contours near edge')
        self._mask_using_contour_groups(self.contour_groups)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Contours near edge removed'))

    def _contour_group_is_near_edge(self, contour_group) -> bool:
        # A contour is a numpy array of (x,y) points
        min_xy = [self._max_pixels_between_contours_in_same_group, self._max_pixels_between_contours_in_same_group]
        max_xy = np.array([self._img.shape[1], self._img.shape[1]]) - self._max_pixels_between_contours_in_same_group

        contour_is_near_edge = [np.any(contour < min_xy) or np.any(contour >= max_xy) for contour in contour_group]
        return any(contour_is_near_edge)

    def _extract_spots(self):
        # Dilate and Erode to 'clean' the spot (nb that this harms the number itself, so we only do it to extract spots)
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

    def _recognise_number_near_each_spot(self):
        self.recognised_numbers = []
        original_image = self._img
        for spot in self.spot_keypoints:
            self._img = original_image
            self._mask_to_contour_groups_close_to(spot.pt, 2*spot.size)
            self._rotate_keypoint_to_bottom_right(spot)
            number = self._recognise_number()

            self.recognised_numbers.append(
                Number(numeric_value=number,
                       dot_location_yx=(spot.pt[1], spot.pt[0]))
            )

    def _mask_to_contour_groups_close_to(self, point_xy, delta):
        nearby_contour_groups = self._extract_contour_groups_close_to(point_xy, delta)
        self._mask_using_contour_groups(nearby_contour_groups)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Neighbourhood of Keypoint'))

    def _extract_contour_groups_close_to(self, target_point_xy, delta):
        contour_groups_near_target = []
        for grp in self.contour_groups:
            # A hack because not all keypoints set the keypoint.size to the radius
            if _dist_from_contour_group(grp, target_point_xy) <= delta:
                contour_groups_near_target.append(grp)

        return contour_groups_near_target

    def _log_contours_on_current_image(self, contours, name):
        img = cv2.cvtColor(self._img.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img, contours, contourIdx=-1, color=(0, 0, 255), thickness=1)
        self.intermediate_images.append(NamedImage(img, name))

    def _mask_using_contour_groups(self, contour_groups):
        remaining_contours = [c for grp in contour_groups for c in grp]
        self._mask_using_contours(remaining_contours)

    def _mask_using_contours(self, contours):
        img = self._img.copy()
        mask = np.zeros(img.shape, np.uint8)
        cv2.drawContours(mask, contours, contourIdx=-1, color=255, thickness=-1)
        img[np.where(mask == 0)] = 255
        self._img = img

    def _rotate_keypoint_to_bottom_right(self, keypoint):
        current_angle = self._estimate_degrees_from_centroid_to_location(y=keypoint.pt[1], x=keypoint.pt[0])
        desired_angle = -30
        self._img = _rotate_image_anticlockwise(desired_angle - current_angle, self._img)
        self.intermediate_images.append(NamedImage(self._img.copy(), 'Rotated Image'))

    def _estimate_degrees_from_centroid_to_location(self, y, x):
        inverted_image = 255 - self._img

        total_intensity = np.sum(inverted_image)
        centroid_y = np.sum(
            np.arange(inverted_image.shape[0]).reshape(-1, 1) * inverted_image) / total_intensity
        centroid_x = np.sum(
            np.arange(inverted_image.shape[1]).reshape(1, -1) * inverted_image) / total_intensity

        return np.rad2deg(np.arctan2(-(y - centroid_y), x - centroid_x))

    def _recognise_number(self) -> int:
        text = self._recognise_number_text()
        return self._extract_number_from_recognised_text(text)

    def _recognise_number_text(self) -> str:
        img = Image.fromarray(self._img)

        # psm 8 => single word;
        # digits => use the digits config file supplied with the software
        return pytesseract.image_to_string(img, config='-psm 8, digits')

    @staticmethod
    def _extract_number_from_recognised_text(recognised_text) -> int:
        # Forcing a terminating period helps us to filter out bad results
        match = re.match(r'(\d+)\.$', recognised_text)

        if match is not None:
            return int(match.group(1))

    def display_intermediate_images(self):
        for img in self.intermediate_images:
            cv2.imshow(winname=img.name, mat=img.image)
            cv2.waitKey(0)

    _default_intermediate_image_save_path_prefix = os.path.join(config.debug_output_folder, 'numrec_')

    @staticmethod
    def delete_intermediate_image_files(save_path_prefix: str = _default_intermediate_image_save_path_prefix):
        for f in glob.glob(save_path_prefix + '*.jpg'):
            os.remove(f)

    def save_intermediate_images(self, save_path_prefix: str = _default_intermediate_image_save_path_prefix):
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


def _compute_contour_distance_matrix(contours):
    contour_distance_matrix = np.zeros([len(contours), len(contours)])
    for i in range(len(contours)):
        for j in range(i + 1, len(contours)):
            contour_distance_matrix[i, j] = _dist_between_contours(contours[i], contours[j])
    contour_distance_matrix = contour_distance_matrix + contour_distance_matrix.T
    return contour_distance_matrix


def _dist_from_contour_group(grp, point_xy):
    return min([_dist_from_contour(cnt, point_xy) for cnt in grp])


def _dist_between_contours(cnt1, cnt2):
    return min([_dist_from_contour(cnt1, pt) for pt in cnt2])


def _dist_from_contour(cnt, point_xy):
    return min(np.linalg.norm(cnt - point_xy, axis=2))


def _rotate_image_anticlockwise(degrees, img):
    # TODO: Change this to pad with white instead of cropping (I think by default it pads with black, so just put in
    # a couple of inverts)
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
