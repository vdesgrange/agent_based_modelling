from enum import Enum

State = Enum('State', 'QUIESCENT ACTIVE JAILED COP')

GraphType = Enum('GraphType', 'ERDOS_RENYI BARABASI_ALBERT WATTS_STROGATZ')


class Color(Enum):
    QUIESCENT = "lightblue"
    ACTIVE = "red"
    JAILED = "lightyellow"
    COP = "black"


class Shape(Enum):
    CITIZEN = "circle"
    COP = "rect"


class HardshipConst(Enum):
    DISTANCE = .5
    TIME_STEP = .1
    TRANSMISSION_RATE = .5
    HARDSHIP = 0
