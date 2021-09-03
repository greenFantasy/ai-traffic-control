from consts import *
from typing import Set

class TrafficLight:
    def __init__(self, movement_options: Set[MovementOptions]):
        self.movement_options: MovementOptions = movement_options
        self.state = TrafficLightStates.red
        self.state_start_time: float = self.get_current_time()

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

    def get_current_time(self):
        # TODO, likely will need to go in a different file
        return None
