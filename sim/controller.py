from trafficlight import TrafficLight
from intersection import Intersection
from consts import *
from typing import List

class Controller:

    def __init__(self, world, intersection, split_times):
        self.num_states: int = 4
        self.world = world
        self.state_start_time: float = 0
        self.state: int = 0
        self.in_termination: bool = True
        self.split_times: List[float] = split_times
        self.intersection: Intersection = intersection
        self.lights: List[List[TrafficLight]] = [[] for i in range(self.num_states)] # list where lights[i] corresponds to lights that should be green in state i
        self._get_lights()

    def _get_lights(self) -> None:
        streets = self.intersection.streets[::2]
        self.lights[0] = [self.intersection.traffic_lights[(streets[0].id, MovementOptions.through)],
                          self.intersection.traffic_lights[(streets[0].id, MovementOptions.right)],
                          self.intersection.traffic_lights[(streets[1].id, MovementOptions.through)],
                          self.intersection.traffic_lights[(streets[1].id, MovementOptions.right)]]

        self.lights[1] = [self.intersection.traffic_lights[(streets[2].id, MovementOptions.left)],
                          self.intersection.traffic_lights[(streets[3].id, MovementOptions.left)],
                          self.intersection.traffic_lights[(streets[0].id, MovementOptions.right)],
                          self.intersection.traffic_lights[(streets[1].id, MovementOptions.right)]]

        self.lights[2] = [self.intersection.traffic_lights[(streets[2].id, MovementOptions.through)],
                          self.intersection.traffic_lights[(streets[2].id, MovementOptions.right)],
                          self.intersection.traffic_lights[(streets[3].id, MovementOptions.through)],
                          self.intersection.traffic_lights[(streets[3].id, MovementOptions.right)]]

        self.lights[3] = [self.intersection.traffic_lights[(streets[0].id, MovementOptions.left)],
                          self.intersection.traffic_lights[(streets[1].id, MovementOptions.left)],
                          self.intersection.traffic_lights[(streets[2].id, MovementOptions.right)],
                          self.intersection.traffic_lights[(streets[3].id, MovementOptions.right)]]

    def is_state_finished(self) -> bool:
        # Checks that lights that were green during state are now red
        return all(l.state == TrafficLightStates.red for l in self.lights[self.state])

    def start_next_state(self) -> None:
        self.state = (self.state + 1) % self.num_states
        for l in self.lights[self.state]:
            l.red_to_green()
        self.in_termination = False
        self.state_start_time = self.world.get_current_time()
        print(f"Switching controller to state {self.state}")

    def get_state_split_time(self) -> float:
        return self.split_times[self.state]

    def control(self) -> None:
        if self.in_termination:
            if self.is_state_finished():
                self.start_next_state()
        else:
            if self.world.get_current_time() - self.state_start_time > self.get_state_split_time():
                for l in self.lights[self.state]:
                    l.green_to_yellow()
                self.in_termination = True
