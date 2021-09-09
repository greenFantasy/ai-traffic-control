from typing import Tuple
from vehicle import Vehicle
from consts import *
from bisect import bisect_left

class Car (Vehicle):
    def __init__(self, rear_left: Tuple[float], height: float, width: float, init_speed: float) -> None:
        super().__init__()
        self.rear_left = rear_left
        self.speed = init_speed
        self.plan = []
        self.height = height
        self.width = width
        self.lane = None

    def get_changing_coordinate(self):
        if not self.lane or Direction.is_north_south(self.lane.direction):
            return self.rear_left[1]
        else:
            return self.rear_left[0]

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

    def move(self, time_step):
        #Recalculate speed at time step depending on distance2nearestobstacle
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        assert self.lane is not None, "Lane is not set - cannot move car"
        # if self.distance2nearestobstacle()>5: #TODO(sssai): implement variable speed depending on distance2nearestobstacle
        if self.lane.direction == Direction.north:
            self.rear_left = (rlX, rlY+self.speed * time_step)
        elif self.lane.direction == Direction.south:
            self.rear_left = (rlX, rlY-self.speed * time_step)
        elif self.lane.direction == Direction.east:
            self.rear_left = (rlX+self.speed * time_step, rlY)
        elif self.lane.direction == Direction.west:
            self.rear_left = (rlX-self.speed * time_step, rlY)
        self.findBoundaries()

    def setLane(self, lane):
        self.lane = lane

    def distance2nearestobstacle(self):
        # Cars can have three obstacles - 
        #   - cars in the same intersection
        #   - cars in the same lane
        #   - red traffic light (in the same street)
        # Firstly, lets get the cars in the same lane:
        assert self.lane, "Cars must have a lane in order to move."
        currLane = self.lane
        vehiclesinLane = currLane.get_vehicles()
        vehiclePos = bisect_left(vehiclesinLane, self)
        assert vehiclePos!=len(vehiclesinLane), "Car is not in the lane's vehicle list"
        if vehiclePos==0:
            # There are no other vehicles in the lane
            closestVehicle = float("inf")
        else:
            carInFront = vehiclesinLane[vehiclePos-1]
            closestVehicle = abs(carInFront.rear_left - carInFront.rear_left)


    
