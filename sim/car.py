from typing import Tuple, List
from vehicle import Vehicle
from consts import *
from bisect import bisect_left
import warnings
import torch
import logger

class Car (Vehicle):
    def __init__(self, center: Tuple[float], height: float, width: float, init_speed: float, id: str) -> None:
        super().__init__()
        self.center = center
        self.speed = init_speed
        self.plan : List[MovementOptions] = [MovementOptions.through] * 10 # TODO: Fix to have actual plan
        self.height = height
        self.width = width
        self.path = None
        self.p_value = None
        self.id = id

    # Efficiency matters - so we define each of the cmp functions
    # TODO(sssai): Not sure if necessary, but should the comparisons make sure the cars are on the same path
    # and for eq
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
        return "Car at (%s,%s)" % (self.center[0], self.center[1])

    def findBoundaries(self):
        self.center: Tuple[float, float] = self.path.parametrization.get_pos(self.p_value)
        center_vec = torch.tensor(self.center)
        forward_vec = torch.tensor(self.path.parametrization.get_direction_vector(self.p_value))
        right_vec = torch.tensor(self.path.parametrization.get_perp_vector(self.p_value))
        # TODO: Boundaries may not be correct?
        self.rear_left = tuple((center_vec - 0.5 * forward_vec - 0.5 * right_vec).tolist())
        self.rear_right = tuple((center_vec - 0.5 * forward_vec + 0.5 * right_vec).tolist())
        self.front_left = tuple((center_vec + 0.5 * forward_vec - 0.5 * right_vec).tolist())
        self.front_right = tuple((center_vec + 0.5 * forward_vec + 0.5 * right_vec).tolist())

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
        if (self.p_value + self.speed*time_step) > self.path.parametrization.max_pos:
            # Move to next path
            connecting_paths = self.path.connecting_paths
            nextPath = None
            if not len(connecting_paths.values())>0:
                # Despawn car 
                logger.logger.logVehicleDespawn(self)
            #TODO(sssai): log when car changes paths (car.id, intersection.id, incoming_path, outgoing_path, wait_time, arrived_on_green, timestamp, etc)
            # Wait Time - instead, just measure time spent on path (Time_spent_on_path) 
            # Also log - Average Speed on Path (Time_spent_on_path / path_length (maxPos))
            # TODO(sssai): Recursively determine if waiting for red light based on car in front 
            elif len(connecting_paths.values()) == 1:
                nextPath = list(connecting_paths.values())[0]
            else:
                nextMoveOp = self.plan.pop(0)
                assert nextMoveOp in connecting_paths, "No path specified for planned move op"
                nextPath = connecting_paths[nextMoveOp]
            # Remove from current path # Assuming that our vehicle is the top of the heap
            self.path.vehicles.pop(-1) # Make sure this works
            if nextPath:
                nextPath.add_vehicle(self, 0)
            else:
                return
        self.setPValue(self.p_value + self.speed*time_step)

    def setPath(self, path):
        self.path = path

    def setPValue(self, p_value):
        self.p_value = p_value
        self.findBoundaries()

    def distance2nearestobstacle(self) -> float:
        # Cars can have two obstacles -
        #   - cars on the same path
        #   - traffic light on the same path
        # First, cars
        assert self.path, "Cars must have a path in order to move."
        currPath = self.path
        vehiclesinPath = currPath.get_vehicles() # TODO(sssai): optimize by using get_vehicles to just get the vehicles in front of the car (smaller p-value)
        vehiclePos = bisect_left(vehiclesinPath, self)
        assert vehiclePos!=len(vehiclesinPath), "Car is not in the path's vehicle list"
        if vehiclePos==0:
            # This is the first vehicle in the path
            distclosestVehicle = float("inf")
        else:
            carInFront = vehiclesinPath[vehiclePos-1]
            distclosestVehicle = abs(carInFront.p_value - self.p_value)
        # Second, traffic lights
        nextMove = self.plan[0]
        if not currPath.traffic_light[nextMove]:
            # No traffic light at end of path
            distclosestTrafficLight =  float("inf")
        elif currPath.traffic_light[nextMove].state == TrafficLightStates.red:
            # closest traffic light is at end of path
            distclosestTrafficLight = currPath.parametrization.max_pos - self.p_value
        else:
            # No traffic light at end of path
            distclosestTrafficLight =  float("inf")
        return min(distclosestVehicle, distclosestTrafficLight)
