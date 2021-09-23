from enum import Enum
from typing import Tuple

class Direction(Enum):
    north = 0
    south = 1
    east = 2
    west = 3

    def is_north_south(direction):
        return direction == Direction.north or direction == Direction.south

class MovementOptions(Enum):
    through = 0
    right = 1
    left = 2

class TrafficLightStates(Enum):
    green = 0
    yellow = 1
    red = 2

STANDARD_LANE_WIDTH = 12.0

def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)