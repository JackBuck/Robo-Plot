import cv2
import numpy as np

import roboplot.dottodot.clustering as clustering


def extract_black_contours(img):
    """
    Extract contours for black objects on a white background.

    Args:
        img (np.ndarray): the (black and white?) image

    Returns:
        list[np.ndarray]: the contours
    """
    img_inverted = 255 - img
    _, contours, _ = cv2.findContours(img_inverted, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    return contours


# TODO: A ContourGroups class would make this cleaner


def group_contours(contours,  min_dist_between_items_in_different_groups):
    """
    Apply single-linkage clustering to group nearby contours.

    Args:
        contours (list[np.ndarray]): a list of contours
        min_dist_between_items_in_different_groups (float): the minimum difference between clusters of contours

    Returns:
        list[list[np.ndarray]]: a list of clusters of contours

    """
    return clustering.group_objects(contours, dist_between_contours, min_dist_between_items_in_different_groups)


def extract_contour_groups_close_to(contour_groups, target_point_xy, delta):
    """
    Extract all groups of contours near some target point.

    Args:
        contour_groups (list[list[np.ndarray]]): a collection of all available groups of contours
        target_point_xy: the point (y,x) near to which all returned contours will lie
        delta (float): groups of contours which contain some contour at least this close to the target point will be
                       returned

    Returns:
        list[list[np.ndarray]]: all groups of contours near to the target point
    """
    contour_groups_near_target = []  # type: list[list[np.ndarray]]
    for grp in contour_groups:
        if dist_from_contour_group(grp, target_point_xy) <= delta:
            contour_groups_near_target.append(grp)

    return contour_groups_near_target


def mask_using_contour_groups(img, contour_groups):
    """
    Return a copy of the supplied image, where all regions outside the supplied contours have been masked to white.

    Args:
        img (np.ndarray): the original image
        contour_groups (list[list[np.ndarray]]): a list of groups of contours to use when masking

    Returns:
        np.ndarray: the masked image
    """
    remaining_contours = [c for grp in contour_groups for c in grp]
    return mask_using_contours(img, remaining_contours)


def mask_using_contours(img, contours):
    """
    Return a copy of the supplied image, where all regions outside the supplied contours have been masked to white.

    Args:
        img (np.ndarray): the original image
        contours (list[np.ndarray]): a list of contours to use when masking

    Returns:
        np.ndarray: the masked image
    """
    img = img.copy()
    mask = np.zeros(img.shape, np.uint8)
    cv2.drawContours(mask, contours, contourIdx=-1, color=255, thickness=-1)
    img[np.where(mask == 0)] = 255
    return img


def dist_from_contour_group(grp, point_xy):
    """
    The smallest realised Euclidean distance between a point and a group of contours.

    Args:
        grp (list[np.ndarray]): the group of contours
        point_xy: a point, specified as (x,y) (NOTE that this is different to the (y,x) convention)

    Returns:
        float: the Euclidean distance between the point and the group of contours.
    """
    return min([dist_from_contour(cnt, point_xy) for cnt in grp])


def dist_between_contours(cnt1, cnt2):
    """
    The Euclidean distance between a pair of contours.

    Args:
        cnt1 (np.ndarray): the first contour (nx2)
        cnt2 (np.ndarray): the second contour (mx2)

    Returns:
        float: the shortest distance between some point in the first contour, and some point in the second.
    """
    return min([dist_from_contour(cnt1, pt) for pt in cnt2])


def dist_from_contour(cnt, point_xy):
    """
    The Euclidean distance between a point and a contour.

    Args:
        cnt (np.ndarray): the first contour (nx2)
        point_xy: a point, specified as (x,y) (NOTE that this is different to the (y,x) convention)

    Returns:
        float: the shortest distance between the specified point and some point on the contour
    """
    return min(np.linalg.norm(cnt - point_xy, axis=2))
