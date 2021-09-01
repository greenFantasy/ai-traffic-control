from consts import *
from lane import Lane
from typing import List

class Street:
    def __init__(self, direction: Direction, lanes: List[Lane]):
        ## TODO: Should we create the lanes in the init?
        self.direction = direction
        self.lanes = lanes
