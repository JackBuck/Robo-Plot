import cv2
import numpy as np

import roboplot.dottodot.clustering as clustering


def extract_black_contours(img) -> list:
    """
    Extract contours for black objects on a white background.

    Args:
        img: the (black and white?) image

    Returns:
        list[np.ndarray]: the contours
    """
    img_inverted = 255 - img
    _, contours, _ = cv2.findContours(img_inverted, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    return contours


# TODO: A ContourGroups class would make this cleaner


def group_contours(contours,  min_dist_between_items_in_different_groups) -> list:
    return clustering.group_objects(contours, dist_between_contours, min_dist_between_items_in_different_groups)


def extract_contour_groups_close_to(contour_groups, target_point_xy, delta):
    contour_groups_near_target = []
    for grp in contour_groups:
        if dist_from_contour_group(grp, target_point_xy) <= delta:
            contour_groups_near_target.append(grp)

    return contour_groups_near_target


def mask_using_contour_groups(img, contour_groups):
    remaining_contours = [c for grp in contour_groups for c in grp]
    return mask_using_contours(img, remaining_contours)


def mask_using_contours(img, contours):
    img = img.copy()
    mask = np.zeros(img.shape, np.uint8)
    cv2.drawContours(mask, contours, contourIdx=-1, color=255, thickness=-1)
    img[np.where(mask == 0)] = 255
    return img


def dist_from_contour_group(grp, point_xy):
    return min([dist_from_contour(cnt, point_xy) for cnt in grp])


def dist_between_contours(cnt1, cnt2):
    return min([dist_from_contour(cnt1, pt) for pt in cnt2])


def dist_from_contour(cnt, point_xy):
    return min(np.linalg.norm(cnt - point_xy, axis=2))
