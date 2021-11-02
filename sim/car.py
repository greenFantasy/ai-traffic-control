from typing import Tuple, List

from vehicle import Vehicle
from consts import *
from bisect import bisect_left
import warnings
import torch
import random
import logger

class Car (Vehicle):
    def __init__(self, center: Tuple[float], height: float, width: float, init_speed: float, id: str) -> None:
        super().__init__()
        self.center = center
        self.speed = init_speed
        self.top_speed = 60 # 60 ft/sec is approximately 40mph
        self.accel_param = 0.1
        self.plan : List[MovementOptions] = []
        self.height = height
        self.width = width
        self.path = None
        self.time_path_entered = 0
        self.despawned = False
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
        return -self.p_value < -other.p_value

    def __le__(self, other):
        return -self.p_value <= -other.p_value

    def __gt__(self, other):
        return -self.p_value > -other.p_value

    def __ge__(self, other):
        return -self.p_value >= -other.p_value

    def __repr__(self):
        return self.id

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

    def move(self, time_step, world):
        if self.despawned:
            return
        #Recalculate speed at time step depending on distance2nearestobstacle
        assert self.path is not None, "Path is not set - cannot move car"
        d = self.distance2nearestobstacle()
        desired_speed = max(min(min((d - 10) / 2.0, self.top_speed), self.path.speed_limit), 0)
        ap = 0.9 if desired_speed < 10 else self.accel_param * time_step
        self.speed = self.speed + ap * (desired_speed - self.speed)

        if (self.p_value + self.speed*time_step) >= self.path.parametrization.max_pos:
            #First, log the the path exit
            logger.logger.logVehiclePathExit(self, self.path, self.time_path_entered)
            # Move to next path
            connecting_paths = self.path.connecting_paths
            nextPath = None
            if not len(connecting_paths.values())>0:
                # Despawn car
                logger.logger.logVehicleDespawn(self)
                self.despawned = True
                world.vehicles.remove(self)
            # Wait Time - instead, just measure time spent on path (Time_spent_on_path)
            # Also log - Average Speed on Path (Time_spent_on_path / path_length (maxPos))
            # TODO(sssai): log when car changes paths (car.id, intersection.id, incoming_path, outgoing_path, wait_time, arrived_on_green, timestamp, etc)
            # TODO(sssai): Recursively determine if waiting for red light based on car in front
            elif len(connecting_paths.values()) == 1:
                nextPath = list(connecting_paths.values())[0]
            else:
                nextMoveOp = self.plan.pop(0)
                assert nextMoveOp in connecting_paths, "No path specified for planned move op"
                nextPath = connecting_paths[nextMoveOp]
            # Remove from current path # Assuming that our vehicle is the top of the heap
            old_path = self.path
            assert self.path.get_vehicles()[-1].id == self.id, f"Car {self.id} is not last in path list: {self.path.get_vehicles()}"
            self.path.vehicles.pop(-1) # Make sure this works
            if nextPath:
                nextPath.add_vehicle(self, (self.p_value + self.speed*time_step) - old_path.parametrization.max_pos)
            else:
                return
        else:
            #print(self.p_value + self.speed*time_step)
            self.setPValue(self.p_value + self.speed*time_step)

    def setPath(self, path):
        if not self.path:
            # Spawn Vehicle
            logger.logger.logVehicleSpawn(self)
        self.path = path
        if len(self.plan) == 0:
            curr_path = path
            while len(curr_path.connecting_paths) > 0:
                idx = random.randint(0, len(curr_path.connecting_paths) - 1)
                self.plan.append(list(curr_path.connecting_paths.keys())[idx])
                curr_path = curr_path.connecting_paths[self.plan[-1]]
        self.time_path_entered = logger.logger.world.time

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
        vehiclesinPath.sort(key= lambda x: x.p_value) # TODO(sssai): why isn't it sorted by default??
        try:
            vehiclePos = vehiclesinPath.index(self) #TODO(sssai): change to binary search i.e. vehiclePos = bisect_left(vehiclesinPath, self)
        except ValueError:
            raise AssertionError(f"Car {self.id} is not in the path's vehicle list: {[(vehicle.id,vehicle.p_value) for vehicle in vehiclesinPath]}")
        if vehiclePos==len(vehiclesinPath)-1:
            # This is the last vehicle in the path
            distclosestVehicle = float("inf")
        else:
            carInFront = vehiclesinPath[vehiclePos+1]
            distclosestVehicle = carInFront.p_value - self.p_value
            assert distclosestVehicle!=0, f"Cars {carInFront} and {self} are are the exact same position. Undefined behaivior"
            assert distclosestVehicle > 0, f"negative distance {distclosestVehicle}, {vehiclesinPath[0].p_value, self.p_value, vehiclePos}"
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
        # Third, check the paths ahead for cars
        connecting_paths = self.path.connecting_paths
        nextPath = None
        distEndPath = currPath.parametrization.max_pos - self.p_value
        distclosestVehicleinNextPath = float("inf")
        if not len(connecting_paths.values())>0:
            nextPath = None
        elif len(connecting_paths.values()) == 1:
            nextPath = list(connecting_paths.values())[0]
        else:
            assert nextMove in connecting_paths, "No path specified for planned move op"
            nextPath = connecting_paths[nextMove]
        if nextPath and len(nextPath.get_vehicles())>0:
            # get first vehicle in path
            firstVehicle = nextPath.get_vehicles()[0]
            distclosestVehicleinNextPath = distEndPath + firstVehicle.p_value
        return min([distclosestVehicle, distclosestTrafficLight, distclosestVehicleinNextPath])
