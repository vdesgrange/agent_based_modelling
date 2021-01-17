def get_average_number_neighbours(density, vision):
    """

    :param density: population density
    :param vision: vision in 4 directions N/S/E/W
    :return: expected number of neighbours: 4 * number of cells per direction * population density
    """
    return 4 * vision * density