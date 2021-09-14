from consts import *
import heapq
from typing import Optional, Dict
from trafficlight import TrafficLight
from parametrization import *

class Path:
    def __init__(self, parametrization: Parametrization, width):
        self.parametrization = parametrization
        self.width = width
        self.start = self.parametrization.get_pos(0) # Starting coordinates
        self.end = self.parametrization.get_pos(self.parametrization.max_pos) # Ending coordinates
        self.vehicles = []
        self.traffic_light: Dict[MovementOptions, TrafficLight] = {MovementOptions.left: None,MovementOptions.through: None, MovementOptions.right: None}
        self.connecting_paths: Dict[MovementOptions, Path] =  {}
        self.street = None

    def add_connecting_path(self, path, moveOp):
        # TODO: connect path and self
        self.connecting_paths[moveOp] = path

    def add_traffic_light(self, traffic_light: TrafficLight, movementOp: MovementOptions):
        self.traffic_light[movementOp] = traffic_light

    def get_vehicles(self, startP: Optional[float] = None, endP: Optional[float] = None):
        heapq.heapify(self.vehicles)
        start = startP if startP else 0
        end = endP if endP else self.parametrization.max_pos
        return [vehicle for vehicle in self.vehicles if end>=vehicle.p_value>=start]

    def add_vehicle(self, vehicle, pos=0):
        # TODO: add vehicle to a position along this path
        # Set path in vehicle so it knows where it is.
        vehicle.setPath(self)
        vehicle.setPValue(pos)
        # Ensure vehicle is in the path - TODO: vehicles don't have position anymore??
        # Add vehicle to vehicle list
        heapq.heappush(self.vehicles, vehicle)
