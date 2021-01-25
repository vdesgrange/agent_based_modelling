from enum import Enum

GRID_WIDTH = GRID_HEIGHT = 10

State = Enum('State', 'QUIESCENT ACTIVE JAILED COP')

GraphType = Enum('GraphType', 'ERDOS_RENYI BARABASI_ALBERT WATTS_STROGATZ')

class Color(Enum):
    QUIESCENT = "lightblue"  # blue
    ACTIVE = "red"  # purple
    JAILED = "lightyellow"  # light gray
    COP = "black" #red


class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"


class HardshipConst(Enum):
    DISTANCE = .5
    TIME_STEP = .1
    TRANSMISSION_RATE = .5
    HARDSHIP = 0
