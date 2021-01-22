from enum import Enum

GRID_WIDTH = GRID_HEIGHT = 10

State = Enum('State', 'QUIESCENT ACTIVE JAILED COP')

GraphType = Enum('GraphType', 'ERDOS_RENYI BARABASI_ALBERT WATTS_STROGATZ')

class Color(Enum):
    QUIESCENT = "#138AF2"  # blue
    ACTIVE = "#AB05F2"  # purple
    JAILED = "#D7E4EF"  # light gray
    COP = "#FF0000" #red


class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"


class HardshipConst(Enum):
    DISTANCE = .5
    TIME_STEP = .1
    TRANSMISSION_RATE = .5
    HARDSHIP = 0


Configuration = dict({
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "max_iter": 1000,
    "max_jail_term": 1000,
    "k": 2.3,
    # "graph_type": GraphType.BARABASI_ALBERT,   # Possibilities: ERDOS_RENYI, BARABASI_ALBERT, WATTS_STROGATZ
    "p": 0.1,  # Determines number of degrees of a node, average number of degrees = p * (total_nodes - 1)
    "p_ws": 0.1,   # Probability rewiring in Watts-Strogatz model (amount of far away connections)
    "directed": False,
    "seed": 1,
})