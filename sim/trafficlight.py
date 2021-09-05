from consts import *
from typing import Set

class TrafficLight:
    def __init__(self, movement_options: MovementOptions, street_direction: Direction, intersection):
        self.movement_option: MovementOptions = movement_options
        self.street_direction: Direction = street_direction
        self.intersection = intersection
        self.state: TrafficLightStates = TrafficLightStates.red
        self.state_start_time: float = self.get_current_time()
        self.pos_x = None
        self.pos_y = None
        self.sensor: Sensor = None

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
        lanes = self.intersection.street_dict[self.street_direction].lanes
        data = []
        for l in lanes:
            data.extend(l.get_vehicles()) # TODO: filter out for vehicles in a certain range

    def get_current_time(self):
        # TODO, likely will need to go in a different file
        return None
