from typing import Tuple, List

from vehicle import Vehicle
from consts import *
from bisect import bisect_left
import warnings
import torch
import random
import logger

# TODO: Move this global to a better location (i.e. this is a parameter of the reward function so defining it here is bad practice).
INTERSECTION_ENTRANCE_THRESHOLD = 50 

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
        self.wait_time_data = None

    # Efficiency matters - so we define each of the cmp functions
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
        # center_vec = torch.tensor(self.center)
        # forward_vec = torch.tensor(self.path.parametrization.get_direction_vector(self.p_value))
        # right_vec = torch.tensor(self.path.parametrization.get_perp_vector(self.p_value))
        # # TODO: Boundaries may not be correct?
        # self.rear_left = tuple((center_vec - 0.5 * forward_vec - 0.5 * right_vec).tolist())
        # self.rear_right = tuple((center_vec - 0.5 * forward_vec + 0.5 * right_vec).tolist())
        # self.front_left = tuple((center_vec + 0.5 * forward_vec - 0.5 * right_vec).tolist())
        # self.front_right = tuple((center_vec + 0.5 * forward_vec + 0.5 * right_vec).tolist())

    def is_entering_intersection(self, world):
        """
        Checks if the car is inside an intersection so that we can log it. 
        """
        distance, intersection_id = self.distance_to_nearest_intersection()
        is_close = (distance <= INTERSECTION_ENTRANCE_THRESHOLD)
        is_stopped = (distance < float('inf') and (not self.path.sub_path) and self.speed < 1 and self.get_distance_to_nearest_car() < 11)
        if is_close or is_stopped:
            self.arrival_on_green = True
            self.wait_time_data = [intersection_id, world.get_current_time(), None]
            return True
        return False
    
    def leaving_intersection(self, world):
        """
        Logs that a car is leaving an intersection (also logs data about when the car entered that intersection).
        """
        assert self.wait_time_data, "Car was not recorded entering intersection but is being recorded leaving it"
        intersection_id, enter_time, aog_red_time = self.wait_time_data
        leave_time = None if world.ended else world.get_current_time()
        logger.logger.log_vehicle_at_intersection((self.id, intersection_id, enter_time, leave_time, self.arrival_on_green, aog_red_time))
        self.wait_time_data = None
        self.nearest_traffic_light = None
    
    def update_arrival_on_green(self, world):
        if not self.nearest_traffic_light:
            _, self.nearest_traffic_light = self.get_distance_to_nearest_traffic_light()
        self.arrival_on_green = self.arrival_on_green and (self.nearest_traffic_light.state != TrafficLightStates.red)
        if not self.arrival_on_green and self.wait_time_data[2] is None:
            self.wait_time_data[2] = world.get_current_time()

    def move(self, time_step, world):
        if self.despawned:
            return
        
        # Metric related calculations
        if not self.wait_time_data: # Check if we are entering an intersection if we aren't already in one.
            self.is_entering_intersection(world)
        elif self.arrival_on_green: # If we are in intersection and we have arrived on green so far
            self.update_arrival_on_green(world)

        #Recalculate speed at time step depending on distance2nearestobstacle
        assert self.path is not None, "Path is not set - cannot move car"
        d = self.distance2nearestobstacle()
        desired_speed = max(min(min((d - 10) / 2.0, self.top_speed), self.path.speed_limit), 0)
        ap = 0.9 if desired_speed < 10 else self.accel_param * time_step
        self.speed = self.speed + ap * (desired_speed - self.speed)
        # Move to the next path or despawn
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
            else:
                nextMoveOp = self.plan.pop(0)
                assert nextMoveOp in connecting_paths, "No path specified for planned move op"
                nextPath = connecting_paths[nextMoveOp]
            # Remove from current path 
            old_path = self.path
            assert self.path.get_vehicles()[-1].id == self.id, f"Car {self.id} is not last in path list: {self.path.get_vehicles()}"
            self.path.vehicles.pop(-1) # Make sure this works
            # set the car_in_front of the vehicle behind to None
            if self.path.vehicles:
                self.path.vehicles[-1].setCarInFront(None)
            if nextPath:
                # Car is changing paths
                nextPath.add_vehicle(self, plan=None, pos=(self.p_value + self.speed*time_step) - old_path.parametrization.max_pos)
                # If sub_path is True, we are entering the middle of an intersection, 
                # which for us is equivalent to leaving the queue leading up the intersection.
                if nextPath.sub_path: 
                    self.leaving_intersection(world)
            else:
                return
        else:
            #print(self.p_value + self.speed*time_step)
            self.setPValue(self.p_value + self.speed*time_step)


    def setPath(self, path, plan=None):
        if not self.path:
            # Spawn Vehicle
            logger.logger.logVehicleSpawn(self)
        self.path = path
        if plan is not None:
            self.plan = plan
        # if len(self.plan) == 0:
        #     curr_path = path # Path that car is being placed on
        #     while len(curr_path.connecting_paths) > 0:
        #         idx = random.randint(0, len(curr_path.connecting_paths) - 1)
        #         self.plan.append(list(curr_path.connecting_paths.keys())[idx])
        #         curr_path = curr_path.connecting_paths[self.plan[-1]]
        self.time_path_entered = logger.logger.world.time
        # When setting the currentPath, set the next path as well
        self.setNextPath()
    
    def setNextPath(self):
        connecting_paths = self.path.connecting_paths
        if len(self.plan) <= 0:
            self.nextpath = None
        elif not len(connecting_paths.values())>0:
            self.nextpath = None
        else:
            next_move_op = self.plan[0]
            self.nextpath = connecting_paths[next_move_op]

    def setCarInFront(self, vehicle):
        self.car_in_front = vehicle

    def setPValue(self, p_value):
        self.p_value = p_value
        self.findBoundaries()
    
    def distance_to_nearest_intersection(self): # distance to nearest intersection, id of intersection
        total_distance= self.path.parametrization.max_pos - self.p_value
        currpath = self.path
        i = 0
        while not any(currpath.traffic_light.values()):
            if i >= len(self.plan):
                return float("inf"), None
            nextMove = self.plan[i]
            currpath = currpath.connecting_paths[nextMove]
            total_distance += currpath.parametrization.max_pos
            i += 1
        intersection_id = [x for x in currpath.traffic_light.values() if x][0].intersection.id
        return total_distance, intersection_id
    
    def get_distance_to_nearest_traffic_light(self) -> float:
        """
        Returns the distance to the nearest traffic light
        """
        if not self.plan:
            return float("inf"), None
        
        total_distance = self.path.parametrization.max_pos - self.p_value
        currpath = self.path
        i = 0
        while not any(currpath.traffic_light.values()):
            if i >= len(self.plan):
                return float("inf"), None
            nextMove = self.plan[i]
            currpath = currpath.connecting_paths[nextMove]
            total_distance += currpath.parametrization.max_pos
            i += 1
        nextMove = self.plan[i]
        # intersection_id = [x for x in currpath.traffic_light.values() if x][0].intersection.id
        return total_distance, currpath.traffic_light[nextMove]
    
    def get_distance_to_car_on_next_path(self) -> float:
        """
        Returns the distance to the nearest car on the next path
        """
        # get first car on next path
        if not self.nextpath:
            return float("inf")
        distEndPath = self.path.parametrization.max_pos - self.p_value
        vehiclesOnNextPath = self.nextpath.get_vehicles()
        if len(vehiclesOnNextPath) <= 0:
            return float("inf")
        else:
            return distEndPath + vehiclesOnNextPath[0].p_value

    def get_distance_to_nearest_car(self) -> float:
        """
        Returns the distance to the nearest car
        """
        if self.car_in_front:
            return self.car_in_front.p_value - self.p_value
        else:
            return float("inf")

    def distance2nearestobstacle(self) -> float:
        """
        Returns the distance to the nearest obstacle.
        """
        # First, get the cars on the same path
        distance2caronpath = self.get_distance_to_nearest_car()
        # print(distance2caronpath)
        # Second, traffic lights
        distance2trafficLight, self.nearest_traffic_light = self.get_distance_to_nearest_traffic_light()
        # Third, check the paths ahead for cars
        distance2caronnextpath = self.get_distance_to_car_on_next_path()
        return min([
            distance2caronpath, 
            distance2trafficLight if self.nearest_traffic_light and (self.nearest_traffic_light.state == TrafficLightStates.red) else float('inf'), 
            distance2caronnextpath
            ])        
