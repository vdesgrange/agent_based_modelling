from enum import Enum

GRID_WIDTH = GRID_HEIGHT = 5

Layer = Enum('Layer', 'GRID NETWORK')
State = Enum('State', 'QUIESCENT ACTIVE JAILED')


class Color(Enum):
    QUIESCENT = "#138AF2"  # blue
    ACTIVE = "#AB05F2"  # purple
    JAILED = "#D7E4EF"  # light gray


class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"
