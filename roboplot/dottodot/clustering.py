import numpy as np


def group_objects(objects, distance_function, min_dist_between_items_in_different_groups) -> list:
    """
    Group objects into clusters using single-linkage clustering.

    Args:
        objects: the objects to cluster
        distance_function (func): a function accepting two objects and returning the distance between them
        min_dist_between_items_in_different_groups: the clusters returned will be minimal subject to the distance
                                                    between any pair of items from different clusters being at least
                                                    this value.

    Returns:
        list[list[object]]: each element is a group of contours.
    """
    distance_matrix = _compute_distance_matrix(objects, distance_function)

    groups = [[i] for i in objects]

    inds_of_mergeable_pair = _compute_indices_of_one_pair_of_mergeable_groups(distance_matrix,
                                                                              min_dist_between_items_in_different_groups)
    while inds_of_mergeable_pair is not None:
        groups, distance_matrix = _merge_groups(groups,
                                                distance_matrix,
                                                inds_of_mergeable_pair)
        inds_of_mergeable_pair = \
            _compute_indices_of_one_pair_of_mergeable_groups(distance_matrix,
                                                             min_dist_between_items_in_different_groups)

    return groups


def _compute_indices_of_one_pair_of_mergeable_groups(distance_matrix, min_dist_between_items_in_different_groups):
    """
    This function semantically operates on a collection of grouped items.
    It returns a pair of indices corresponding to a pair of groups which are close enough to merge.

    Args:
        distance_matrix (np.ndarray): the matrix containing distances between all groups
        min_dist_between_items_in_different_groups (float): the algorithm will only suggest a pair of groups to be
                                                            merged if they each contain an item which is within this
                                                            value of the other.

    Returns:
        a pair of indices corresponding to a mergeable pair of groups
    """
    # Get all indices (i,j) with i<j, in a 2-element tuple (all rows indices, all column indices).
    inds = np.triu_indices_from(distance_matrix, 1)
    # Get a boolean vector which indexes both elements of inds and tells whether the pair of groups should be merged
    groups_could_be_merged = distance_matrix[inds] < min_dist_between_items_in_different_groups
    # Get the subset of indices for groups we can merge
    inds_of_mergeable_groups = [inds[i][groups_could_be_merged] for i in range(len(inds))]
    # Return the first pair of indices, if any were found
    indices_matrix = np.transpose(inds_of_mergeable_groups)
    return indices_matrix[0] if len(indices_matrix) > 0 else None


def _merge_groups(groups, current_distance_matrix, inds_of_mergeable_pair):
    """
    Merge a pair of groups in a group of objects.

    Args:
        groups (list[list[object]]): the groups of objects (a list of lists)
        current_distance_matrix (np.ndarray): the symmetric matrix of distances between groups
        inds_of_mergeable_pair (indexable): a pair of indices corresponding to the groups to merge

    Returns:
        tuple: The first return value is a new set of groups, with the specified pair of contours merged.
               The second return value is the distance matrix for the new set of groups.
    """
    # Merge the actual groups
    new_groups = groups.copy()
    first_group = new_groups.pop(max(inds_of_mergeable_pair))
    second_group = new_groups.pop(min(inds_of_mergeable_pair))
    new_groups.append(first_group + second_group)

    # Merge rows and columns in the distance matrix
    new_distances = current_distance_matrix[inds_of_mergeable_pair, :].min(axis=0)

    groups_to_keep = np.ones(len(current_distance_matrix), dtype=bool)
    groups_to_keep[inds_of_mergeable_pair] = False

    new_distance_matrix = np.zeros([i-1 for i in current_distance_matrix.shape])
    new_distance_matrix[0:-1, 0:-1] = current_distance_matrix[groups_to_keep,:][:, groups_to_keep]
    new_distance_matrix[-1, 0:-1] = new_distances[groups_to_keep]
    new_distance_matrix[0:-1, -1] = new_distances[groups_to_keep]

    return new_groups, new_distance_matrix


def _compute_distance_matrix(objects, distance_function):
    """
    Compute a distance matrix.

    Args:
        objects (list): the objects whose distance matrix is to be computed
        distance_function (func): a function accepting two objects and returning the distance between them

    Returns:
        np.ndarray: the distance matrix

    """
    contour_distance_matrix = np.zeros([len(objects), len(objects)])
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            contour_distance_matrix[i, j] = distance_function(objects[i], objects[j])
    contour_distance_matrix = contour_distance_matrix + contour_distance_matrix.T
    return contour_distance_matrix

