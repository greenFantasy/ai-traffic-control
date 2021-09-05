from consts import *
from lane import Lane
from typing import List

class Street:
    def __init__(self, direction: Direction, lanes: List[Lane]):
        ## TODO: Should we create the lanes in the init?
        self.direction = direction
        self.lanes = lanes
        self.min = min([lane.min for lane in lanes])
        self.max = max([lane.max for lane in lanes])
        for l in lanes:
            l.street = self
        self.intersections = []
