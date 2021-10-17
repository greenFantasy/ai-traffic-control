from consts import *
# import heapq
from typing import Optional, Dict, List
from trafficlight import TrafficLight
from sensor import Sensor
from parametrization import *
import logger

class Path:
    def __init__(self, parametrization: Parametrization, width, sensors=None, id=None, aux_path=False):
        self.parametrization = parametrization
        self.width = width
        self.start = self.parametrization.get_pos(0) # Starting coordinates
        self.end = self.parametrization.get_pos(self.parametrization.max_pos) # Ending coordinates
        self.vehicles = [] # Vehicles are sorted so those with the highest p-value are last
        self.traffic_light: Dict[MovementOptions, TrafficLight] = {MovementOptions.left: None,MovementOptions.through: None, MovementOptions.right: None}
        self.connecting_paths: Dict[MovementOptions, Path] =  {}
        self.street = None
        self.sensors: List[Sensor] = sensors if sensors else []
        self.id = id #TODO - make this a id related to the street or intersection that the path is part of
        self.aux_path = aux_path

    def __repr__(self):
        return f"Path with id {self.id}"

    def set_id(self, id):
        self.id = id

    def add_connecting_path(self, path, moveOp):
        # TODO: connect path and self
        self.connecting_paths[moveOp] = path

    def add_traffic_light(self, traffic_light: TrafficLight, movementOp: MovementOptions):
        self.traffic_light[movementOp] = traffic_light

    def get_vehicles(self, startP: Optional[float] = None, endP: Optional[float] = None):
        start = startP if startP else 0
        end = endP if endP else self.parametrization.max_pos
        return [vehicle for vehicle in self.vehicles if end>=vehicle.p_value>=start]

    def add_vehicle(self, vehicle, pos=0):
        # Set path in vehicle so it knows where it is.
        if len(self.vehicles) > 0 and isclose(self.vehicles[0].p_value,pos, abs_tol=0.001): # self.vehicles[0].height:
            print("Failed to add vehicle")
            return False
        vehicle.setPath(self)
        vehicle.setPValue(pos)
        # Ensure vehicle is in the path boundaries - TODO: vehicles don't have position anymore??
        # Add vehicle to vehicle list
        # self.vehicles.append(vehicle)
        self.vehicles.insert(0, vehicle)
        #self.vehicles.sort(key = lambda x: x.p_value)
        return True

    def add_sensor(self, p_min=None, p_max=None, sensor_type='binary'):
        p_min = p_min if p_min else self.parametrization.max_pos - 40
        p_max = p_max if p_max else p_min + 35
        assert p_min >= 0 and p_max <= self.parametrization.max_pos
        self.sensors.append(Sensor(self, p_min, p_max, sensor_type))
