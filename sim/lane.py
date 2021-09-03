from consts import *

class Lane:
    def __init__(
        self,
        direction: Direction,
        position: float,
        width: float,
        start: float = None,
        end: float = None
    ):
        self.direction = direction
        self.position = position
        self.width = width
        self.start = start
        self.end = end
        self.vehicles = []
        self.min = self.position - self.width / 2
        self.max = self.position + self.width / 2

    def add_vehicle(self, ):
        # TODO
        pass
