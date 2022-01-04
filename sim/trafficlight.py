from consts import *
from typing import Set
from sensor import Sensor
import logger

class TrafficLight:
    def __init__(self, movement_options: MovementOptions, street_id, intersection, traffic_light_id: str, yellow_to_red_time: float = 2.0):
        self.movement_option: MovementOptions = movement_options # TODO(rajatmittal): what is this used for
        self.street_id: int = street_id
        self.intersection = intersection
        self.state: TrafficLightStates = TrafficLightStates.red
        self.state_start_time: float = 0.0 # self.get_current_time()
        self.id = traffic_light_id
        self.yellow_to_red_time = yellow_to_red_time
        self.controlling_paths = []

    def check_yellow_to_red(self, curr_time):
        if self.state == TrafficLightStates.yellow and curr_time - self.state_start_time > self.yellow_to_red_time:
            self.yellow_to_red(curr_time)

    def green_to_yellow(self, curr_time):
        assert(self.state == TrafficLightStates.green)
        self.state = TrafficLightStates.yellow
        self.state_start_time = curr_time
        logger.logger.logTrafficLightChange(self, TrafficLightStates.green, TrafficLightStates.yellow)

    def yellow_to_red(self, curr_time):
        assert(self.state == TrafficLightStates.yellow)
        self.state = TrafficLightStates.red
        self.state_start_time = curr_time
        logger.logger.logTrafficLightChange(self, TrafficLightStates.yellow, TrafficLightStates.red)

    def red_to_green(self, curr_time):
        assert(self.state == TrafficLightStates.red)
        self.state = TrafficLightStates.green
        self.state_start_time = curr_time
        logger.logger.logTrafficLightChange(self, TrafficLightStates.red, TrafficLightStates.green)

    def add_path(self, path, moveOp):
        self.controlling_paths.append((path,moveOp))
