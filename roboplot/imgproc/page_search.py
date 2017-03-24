def compute_perimeter_positions(width, height, photo_size):
    """Finds the positions needed for the camera to capture the entire border of page.
    
    Args:
        width (int): The width of the paper (x axis).
        height (int): The height of the paper (y axis).
        photo_size (int): The size of the square photo in mm
        
    Returns:
        positions (list of points) The path required to scan border of the page.
    """

    positions = []
    current_path_point = (int(photo_size / 2), int(photo_size / 2))
    max_x_pos = width - int(photo_size / 2)
    max_y_pos = height - int(photo_size / 2)

    # Keep y at 0 and move along edge increasing in x.
    while current_path_point[0] < max_y_pos:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0] + photo_size, current_path_point[1])

    current_path_point = (max_y_pos, current_path_point[1])

    # Keep x max and move along edge increasing in y
    while current_path_point[1] < max_x_pos:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0], current_path_point[1] + photo_size)

    current_path_point = (current_path_point[0], max_x_pos)

    # Keep y max and move along edge decreasing in x
    while current_path_point[0] > photo_size / 2:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0] - photo_size, current_path_point[1])

    current_path_point = (int(photo_size / 2), max_x_pos)

    # Keep x = 0 and move along edge decreasing in y
    while current_path_point[1] > photo_size / 2:
        positions.append(current_path_point)
        current_path_point = (current_path_point[0], current_path_point[1] - photo_size)

    return positions


def compute_positions(width: int, height: int, photo_size: int, distance_between_photos: int = None):
    """Finds the positions needed for the camera to capture the entire page.
    
    Args:
        width (int): The width of the paper (x axis).
        height (int): The height of the paper (y axis).
        photo_size (int): The size of the square photo in mm.
        distance_between_photos (int): The distance in mm used to offset consecutive photos. If left as None, then the
                                       photo_size will be used instead.

    Returns:
        positions (list of points) The path required to scan entire page.
    """

    if distance_between_photos is None:
        distance_between_photos = photo_size

    positions = []
    current_path_point = [int(photo_size / 2), int(photo_size / 2)]

    # Set up min/max positions for camera to view entire page.
    max_x_pos = width - int(photo_size / 2)
    max_y_pos = height - int(photo_size / 2)

    last_row = False

    # Increment y.
    while not last_row:

        if current_path_point[0] == max_y_pos:
            last_row = True

        # Increment x.
        while current_path_point[1] < max_x_pos:
            positions.append(current_path_point.copy())
            current_path_point[1] += distance_between_photos

        current_path_point[1] = max_x_pos
        positions.append(current_path_point.copy())

        # Increment y once.   
        if last_row:
            break
        elif current_path_point[0] + distance_between_photos > max_y_pos:
            current_path_point[0] = max_y_pos
            last_row = True
        else:
            current_path_point[0] += distance_between_photos

        # Decrement x.
        while current_path_point[1] > int(photo_size / 2):
            positions.append(current_path_point.copy())
            current_path_point[1] -= distance_between_photos

        current_path_point[1] = int(photo_size / 2)
        positions.append(current_path_point.copy())

        current_path_point[0] += distance_between_photos

        if current_path_point[0] > max_y_pos:
            current_path_point[0] = max_y_pos

    return positions
