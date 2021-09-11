from enum import Enum
from collections.abc import Callable

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

class Parametrization:
    def __init__(self,
        name: str,
        coor_func: Callable[[float], Tuple[float, float]],
        max_pos: float,
        starting_coors: Tuple[float, float]=(0, 0)
    ):

        assert(len(coor_func(0)) == 2) # coor_func must return a length 2 tuple
        self.name = name
        self.coor_func: Callable[[float], Tuple[float, float]] = coor_func
        self.max_pos: float = max_pos # cannot feed in pos > max_pos into coor_func
        self.starting_coors = starting_coors

    def get_pos(self, p) -> Tuple[float, float]:
        # get position associated with p
        if p > self.max_pos:
            raise ValueError(f'p = {p} > max_pos allowed for {self.name} parametrization')

        (x, y) = self.coor_func(p)
        return (x + self.starting_coors[0], y + self.starting_coors[1])

    def get_direction_vector(self, p) -> Tuple[float, float]:
        # TODO: get direction vector associated with a specific position along the path, to determine which angle the vehicle should be facing
        pass


STANDARD_LANE_WIDTH = 12.0
