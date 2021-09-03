from typing import Tuple
from vehicle import Vehicle
from consts import *

class Car (Vehicle):
    def __init__(self, rear_left: Tuple[float], height: float, width: float, direction: Direction) -> None:
        super().__init__()
        self.rear_left = rear_left
        self.speed = 0
        self.plan = []
        self.height = height
        self.width = width
        self.direction = direction
        self.findBoundaries()

    def findBoundaries(self):
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        if self.direction == Direction.north:
            self.rear_right = (rlX + self.width, rlY)
            self.front_left = (rlX, rlY + self.height)
            self.front_right = (rlX + self.width, rlY + self.height)
        elif self.direction == Direction.south:
            self.rear_right = (rlX - self.width, rlY)
            self.front_left = (rlX, rlY - self.height)
            self.front_right = (rlX - self.width, rlY - self.height)        
        elif self.direction == Direction.east:
            self.rear_right = (rlX, rlY-self.width)
            self.front_left = (rlX+ self.height, rlY )
            self.front_right = (rlX+ self.height, rlY -self.width)        
        elif self.direction == Direction.west:
            self.rear_right = (rlX, rlY+self.width)
            self.front_left = (rlX-self.height, rlY )
            self.front_right = (rlX- self.height, rlY +self.width)   

    def move(self):
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        if self.distance2nearestobstacle()>5:
            if self.direction == Direction.north:
                self.rear_left = (rlX, rlY+self.speed)
            elif self.direction == Direction.south:
                self.rear_left = (rlX, rlY-self.speed)
            elif self.direction == Direction.east:
                self.rear_left = (rlX+self.speed, rlY)
            elif self.direction == Direction.west:
                self.rear_left = (rlX-self.speed, rlY)
        self.findBoundaries()


    def distance2nearestobstacle(self):
        #TODO
        pass