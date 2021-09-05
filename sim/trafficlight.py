from consts import *
from typing import Set
from sensor import Sensor

class TrafficLight:
    def __init__(self, movement_options: MovementOptions, street_direction: Direction, intersection, sensor):
        self.movement_option: MovementOptions = movement_options
        self.street_direction: Direction = street_direction
        self.intersection = intersection
        self.state: TrafficLightStates = TrafficLightStates.red
        self.state_start_time: float = self.get_current_time()
        self.sensor: Sensor = sensor # TODO: Should be able to have multiple sensors

    def green_to_yellow(self):
        assert(self.state == TrafficLightStates.green)
        self.state = TrafficLightStates.yellow
        self.state_start_time = self.get_current_time()

    def yellow_to_red(self):
        assert(self.state == TrafficLightStates.yellow)
        self.state = TrafficLightStates.red
        self.state_start_time = self.get_current_time()

    def red_to_green(self):
        assert(self.state == TrafficLightStates.red)
        self.state = TrafficLightStates.green
        self.state_start_time = self.get_current_time()

    def get_sensor_data(self):
        if not self.sensor:
            return []
        lanes = self.intersection.street_dict[self.street_direction].lanes
        data = []
        for l in lanes:
            if self.street_direction == Direction.north:
                data.extend(l.get_vehicles(self.intersection.lower_boundary - self.sensor.range,self.intersection.upper_boundary))
            elif self.street_direction == Direction.south:
                data.extend(l.get_vehicles(self.intersection.lower_boundary,self.intersection.upper_boundary + self.sensor.range))
            elif self.street_direction == Direction.east:
                data.extend(l.get_vehicles(self.intersection.left_boundary - self.sensor.range,self.intersection.right_boundary))
            else:
                data.extend(l.get_vehicles(self.intersection.left_boundary,self.intersection.right_boundary + self.sensor.range))
        return data

    def get_current_time(self):
        return self.intersection.world.get_current_time()
