import json

def get_average_number_neighbours(density, vision):
    """

    :param density: population density
    :param vision: vision in 4 directions N/S/E/W
    :return: expected number of neighbours: 4 * number of cells per direction * population density
    """
    return 4 * vision * density


def read_configuration(filepath='./configurations/default.json'):
    """
    Read configuration of the model store in json files.
    JSON let us store values of different types (string, int, float, booleans, etc.).
    :param filepath: Relative path to the configuration file
    :return a dictionary of configuration values
    """
    with open(filepath, 'r') as f:
        configuration = json.load(f)

    return configuration
