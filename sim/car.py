from typing import Tuple
from vehicle import Vehicle
from consts import *
from bisect import bisect_left
import warnings

class Car (Vehicle):
    def __init__(self, rear_left: Tuple[float], height: float, width: float, init_speed: float) -> None:
        super().__init__()
        self.rear_left = rear_left
        self.speed = init_speed
        self.plan = []
        self.height = height
        self.width = width
        self.lane = None
        self.id = 0 # TODO(sssai): make this an input to initialize Car 
    
    # Efficiency matters - so we define each of the cmp functions
    def __eq__(self, other):
        return self.get_changing_coordinate() == other.get_changing_coordinate() and self.id == other.id

    def __ne__(self, other):
        return self.get_changing_coordinate() != other.get_changing_coordinate()

    def __lt__(self, other):
        return self.get_changing_coordinate() < other.get_changing_coordinate()

    def __le__(self, other):
        return self.get_changing_coordinate() <= other.get_changing_coordinate()

    def __gt__(self, other):
        return self.get_changing_coordinate() > other.get_changing_coordinate()

    def __ge__(self, other):
        return self.get_changing_coordinate() >= other.get_changing_coordinate()

    def __repr__(self):
        return "Car at (%s,%s)" % (self.rear_left[0], self.rear_left[1])

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
        if self.distance2nearestobstacle()>10:
            self.speed = 30
        elif 5<=self.distance2nearestobstacle()<=10:
            self.speed = 15
        elif 2<=self.distance2nearestobstacle()<=5:
            self.speed = 5
        elif self.distance2nearestobstacle()<=2:
            self.speed = 0
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

    def get_intersection_boundary_by_dir(self, intersection) -> float:
        if self.lane.direction == Direction.north:
            return intersection.lower_boundary
        elif self.lane.direction == Direction.south:
            return intersection.upper_boundary
        elif self.lane.direction == Direction.east:
            return intersection.left_boundary
        elif self.lane.direction == Direction.west:
            return intersection.right_boundary

    def distance2nearestobstacle(self) -> float:
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
            closestVehicle = abs(carInFront.get_changing_coordinate() - self.get_changing_coordinate())
        # Secondly, let's get cars in the same intersection:
        # TODO(sssai)
        closestCarInIntersection = float("inf")
        # Thirdly, let's find the nearest intersection with a red light:
        currStreet = currLane.street
        assert currStreet, f"Lane {currLane} is not in a street"
        nearestIntersection = currStreet.intersections[0] # TODO(sssai) actually get the nearest intersection once it's a heap
        if self.plan ==[]:
            warnings.warn("Car has no plan - defaulting to Move.through")
            nextMove = MovementOptions.through
        else:
            nextMove = self.plan[0]
        currTrafficLight = nearestIntersection.traffic_lights[(currLane.direction, nextMove)]
        if currTrafficLight.state != TrafficLightStates.red:
            closestIntersection = float("inf")
        else:
            diffIntersection = self.get_intersection_boundary_by_dir(nearestIntersection) - self.get_changing_coordinate()
            if currLane.direction == Direction.north or currLane.direction == Direction.east:
                if diffIntersection >= 0:
                    closestIntersection = diffIntersection
                else:
                    closestIntersection = float("inf")
            elif currLane.direction == Direction.south or currLane.direction == Direction.west:
                if diffIntersection <= 0:
                    closestIntersection = abs(diffIntersection)
                else:
                    closestIntersection = float("inf")
        return min([closestVehicle, closestCarInIntersection, closestIntersection])


    
