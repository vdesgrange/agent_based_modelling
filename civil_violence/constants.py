from enum import Enum

GRID_WIDTH = GRID_HEIGHT = 10

State = Enum('State', 'QUIESCENT ACTIVE JAILED COP')

GraphType = Enum('GraphType', 'ERDOS_RENYI')


class Color(Enum):
    QUIESCENT = "#138AF2"  # blue
    ACTIVE = "#AB05F2"  # purple
    JAILED = "#D7E4EF"  # light gray
    COP = "#FF0000" #red




class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"
