from typing import Tuple
from vehicle import Vehicle
from consts import *

class Car (Vehicle):
    def __init__(self, rear_left: Tuple[float], height: float, width: float) -> None:
        super().__init__()
        self.rear_left = rear_left
        self.speed = 0
        self.plan = []
        self.height = height
        self.width = width
        self.lane = None

    def findBoundaries(self):
        # Add center calculations self.center
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        assert self.lane is not None, "Lane is not set - cannot calculate boundary of car"
        if self.lane.direction == Direction.north:
            self.rear_right = (rlX + self.width, rlY)
            self.front_left = (rlX, rlY + self.height)
            self.front_right = (rlX + self.width, rlY + self.height)
        elif self.lane.direction == Direction.south:
            self.rear_right = (rlX - self.width, rlY)
            self.front_left = (rlX, rlY - self.height)
            self.front_right = (rlX - self.width, rlY - self.height)        
        elif self.lane.direction == Direction.east:
            self.rear_right = (rlX, rlY-self.width)
            self.front_left = (rlX+ self.height, rlY )
            self.front_right = (rlX+ self.height, rlY -self.width)        
        elif self.lane.direction == Direction.west:
            self.rear_right = (rlX, rlY+self.width)
            self.front_left = (rlX-self.height, rlY )
            self.front_right = (rlX- self.height, rlY +self.width)   

    def move(self):
        #Recalculate speed at time step depending on distance2nearestobstacle
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        assert self.lane is not None, "Lane is not set - cannot move car"
        if self.distance2nearestobstacle()>5:
            if self.lane.direction == Direction.north:
                self.rear_left = (rlX, rlY+self.speed)
            elif self.lane.direction == Direction.south:
                self.rear_left = (rlX, rlY-self.speed)
            elif self.lane.direction == Direction.east:
                self.rear_left = (rlX+self.speed, rlY)
            elif self.lane.direction == Direction.west:
                self.rear_left = (rlX-self.speed, rlY)
        self.findBoundaries()

    def setLane(self, lane):
        self.lane = lane

    def distance2nearestobstacle(self):
        #TODO
        pass

    