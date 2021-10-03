from consts import *
from typing import Set
from sensor import Sensor
import logger

class TrafficLight:
    def __init__(self, movement_options: MovementOptions, street_id, intersection, traffic_light_id: str, yellow_to_red_time: float = 2.0):
        self.movement_option: MovementOptions = movement_options
        self.street_id: int = street_id
        self.intersection = intersection
        self.state: TrafficLightStates = TrafficLightStates.red
        self.state_start_time: float = self.get_current_time()
        self.id = traffic_light_id
        self.yellow_to_red_time = yellow_to_red_time

    def check_yellow_to_red(self):
        if self.state == TrafficLightStates.yellow and self.get_current_time() - self.state_start_time > self.yellow_to_red_time:
            self.yellow_to_red()

    def green_to_yellow(self):
        assert(self.state == TrafficLightStates.green)
        self.state = TrafficLightStates.yellow
        self.state_start_time = self.get_current_time()
        logger.logger.logTrafficLightChange(self, TrafficLightStates.green, TrafficLightStates.yellow)

    def yellow_to_red(self):
        assert(self.state == TrafficLightStates.yellow)
        self.state = TrafficLightStates.red
        self.state_start_time = self.get_current_time()
        logger.logger.logTrafficLightChange(self, TrafficLightStates.yellow, TrafficLightStates.red)

    def red_to_green(self):
        assert(self.state == TrafficLightStates.red)
        self.state = TrafficLightStates.green
        self.state_start_time = self.get_current_time()
        logger.logger.logTrafficLightChange(self, TrafficLightStates.red, TrafficLightStates.green)

    def get_current_time(self):
        return self.intersection.world.get_current_time()
