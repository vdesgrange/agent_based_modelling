from enum import Enum

GRID_WIDTH = GRID_HEIGHT = 40

Layer = Enum('Layer', 'GRID NETWORK')
State = Enum('State', 'QUIESCENT ACTIVE JAILED')


class Color(Enum):
    QUIESCENT = "#138AF2"  # blue
    ACTIVE = "#AB05F2"  # purple
    JAILED = "#FFFFFF"


class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"
