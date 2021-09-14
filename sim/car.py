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
        self.path = None
        self.p_value = None
        self.id = 0 # TODO(sssai): make this an input to initialize Car 
    
    # Efficiency matters - so we define each of the cmp functions
    def __eq__(self, other):
        return self.p_value == other.p_value and self.id == other.id

    def __ne__(self, other):
        return self.p_value != other.p_value

    def __lt__(self, other):
        return self.p_value < other.p_value

    def __le__(self, other):
        return self.p_value <= other.p_value

    def __gt__(self, other):
        return self.p_value > other.p_value

    def __ge__(self, other):
        return self.p_value >= other.p_value

    def __repr__(self):
        return "Car at (%s,%s)" % (self.rear_left[0], self.rear_left[1])

    def findBoundaries(self): # Can't do this anymore - tf is a derivative 
        # Add center calculations self.center
        rlX : float = self.rear_left[0]
        rlY : float = self.rear_left[1]
        raise AssertionError("Not implemented with paths - how?")

    def move(self, time_step):
        #Recalculate speed at time step depending on distance2nearestobstacle
        assert self.path is not None, "Path is not set - cannot move car"
        if self.distance2nearestobstacle()>10:
            self.speed = 30
        elif 5<=self.distance2nearestobstacle()<=10:
            self.speed = 15
        elif 2<=self.distance2nearestobstacle()<=5:
            self.speed = 5
        elif self.distance2nearestobstacle()<=2:
            self.speed = 0
        self.p_value += self.speed+time_step
        self.findBoundaries()

    def setPath(self, path):
        self.path = path
    
    def setPValue(self, p_value):
        self.p_value = p_value
        # TODO(sssai): run code to calculate vehicle boundaries

    def distance2nearestobstacle(self) -> float:
        # Cars can have two obstacles - 
        #   - cars on the same path
        #   - traffic light on the same path
        # First, cars
        assert self.path, "Cars must have a path in order to move."
        currPath = self.path
        vehiclesinPath = currPath.get_vehicles() # TODO(sssai): optimize by using get_vehicles to just get the vehiclees in front of the car (smaller p-value)
        vehiclePos = bisect_left(vehiclesinPath, self)
        assert vehiclePos!=len(vehiclesinPath), "Car is not in the path's vehicle list"
        if vehiclePos==0:
            # This is the first vehicle in the path
            closestVehicle = float("inf")
        else:
            carInFront = vehiclesinPath[vehiclePos-1]
            closestVehicle = abs(carInFront.p_value - self.p_value)
        # Second, traffic lights
        # TODO: traffic light code not yet implemented
        closestTrafficLight =  currPath.parametrization.max_p - self.p_value
    
