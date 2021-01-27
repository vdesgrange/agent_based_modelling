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


def hex_to_RGB(hex):
    """
    Convert hexadecimal to RGB
    Original code from https://github.com/fabero/Civil-Violence-Modelling-A05
    """
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
    """
    Convert RGB to hexadecimal
    Original code from https://github.com/fabero/Civil-Violence-Modelling-A05
    """
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                        "{0:x}".format(v) for v in RGB])


def color_dict(gradient):
    """
    Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on.
    Original code from https://github.com/fabero/Civil-Violence-Modelling-A05
    """
    return {"hex": [RGB_to_hex(RGB).upper() for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    """
    Returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    including the number sign ("#FFFFFF").
    Original code from https://github.com/fabero/Civil-Violence-Modelling-A05
    """
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [
            int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
            for j in range(3)
        ]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)


def compute_quiescent(model):
    return model.count_type_citizens("QUIESCENT")


def compute_active(model):
    return model.count_type_citizens("ACTIVE")


def compute_jailed(model):
    return model.count_type_citizens("JAILED")


def compute_legitimacy(model):
    return model.legitimacy


def compute_influencers(model):
    return len(model.influencer_list)


def compute_outbreaks(model):
    return model.outbreaks
