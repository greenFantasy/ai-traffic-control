from consts import *
import heapq
from typing import Optional

class Path:
    def __init__(self, parametrization: Parametrization):
        self.parametrization = parametrization
        self.start = self.parametrization.get_pos(0) # Starting coordinates
        self.end = self.parametrization.get_pos(self.parametrization.max_p) # Ending coordinates
        self.vehicles = [] 
        self.traffic_lights = [] # TODO: I presume a path will have at most two traffic lights - i.e. one at the front one at the back. If so, we shouldn't use a list, just store both as Optionals
    def add_connecting_path(self, path):
        # TODO: connect path and self
        pass

    def add_traffic_light(self, traffic_light, pos):
        # TODO: add traffic light to a position along this path
        pass

    def get_vehicles(self, startP: Optional[float] = None, endP: Optional[float] = None):
        start = startP if startP else -float('inf')
        end = endP if endP else float('inf')
        return [vehicleTup[1] for vehicleTup in self.vehicles if end>=vehicleTup[1].p_value>=start]

    def add_vehicle(self, vehicle, pos):
        # TODO: add vehicle to a position along this path
        # Set lane in vehicle so it knows where it is.
        vehicle.setPath(self)
        vehicle.setPValue(pos)
        # Ensure vehicle is in the lane - TODO: vehicles don't have position anymore??
        # Add vehicle to vehicle list
        heapq.heappush(self.vehicles, (vehicle.p_value,vehicle))
