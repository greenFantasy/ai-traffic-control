from enum import Enum

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
