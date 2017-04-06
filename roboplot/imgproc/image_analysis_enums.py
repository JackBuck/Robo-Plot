import enum


class Centroid(enum.IntEnum):
    VALID = 0
    INVALID_RANGE = 1
    INVALID_NO_WHITE = 2


class Direction(enum.IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


def turn_left(current_direction):
    """

    Args:
        current_direction: The direction the previous picture was taken in.

    Returns:
        new_direction: The direction after turning left
    """
    direction_array = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    direction_index = (current_direction - 1) % 4
    return direction_array[direction_index]


def turn_right(current_direction):
    """"

    Args:
        current_direction: The direction the previous picture was taken in.

    Returns:
        new_direction: The direction after turning right
    """
    direction_array = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    direction_index = (current_direction + 1) % 4
    return direction_array[direction_index]


def turn_around(current_direction):
    """"

    Args:
        current_direction: The direction the previous picture was taken in.

    Returns:
        new_direction: The direction after turning around
    """
    direction_array = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    direction_index = (current_direction + 2) % 4
    return direction_array[direction_index]


class Turning(enum.IntEnum):
    LEFT = 0
    STRAIGHT = 1
    RIGHT = 2
    INVALID = 3
    BLACK_END = 4
