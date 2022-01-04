from trafficlight import TrafficLight
from intersection import Intersection
from consts import *
from typing import List
import torch
import logger
import random

class Controller:

    def __init__(self, world, intersection, split_times):
        self.verbose = False
        self.num_states: int = 4
        self.world = world
        self.state_start_time: float = 0
        self.state: int = 0
        self.next_state: int = 1
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
        self.state = self.next_state
        for l in self.lights[self.state]:
            l.red_to_green(self.world.get_current_time())
        self.in_termination = False
        self.state_start_time = self.world.get_current_time()
        if self.verbose:
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
                    l.green_to_yellow(self.world.get_current_time())
                self.in_termination = True
                self.next_state = (self.state + 1) % self.num_states

class RLController(Controller):

    def __init__(self, world, intersection, num_snapshots: int, greedy_prob: float):
        super().__init__(world, intersection, [])

        self.min_wait_time = 5.0

        self.greedy_prob = greedy_prob # When training, probability with which to take "optimal" actions (as opposed to random actions)

        self.mode='train' # Can be train or eval

        # State calculation
        self.total_snapshots: int = num_snapshots
        self.snapshots: List[torch.tensor] = [self.get_current_snapshot() for _ in range(num_snapshots)]

    def is_training(self):
        return self.mode == 'train'

    def set_model(self, model):
        self.model = model

    def get_action(self, env_state):
        if (not self.is_training()) or random.random() < self.greedy_prob:
            model_input = env_state.unsqueeze(0)
            model_output = self.model.forward(model_input).squeeze(0)
            if self.verbose:
                print(f"Model Predictions: {model_output}")
            next_state = torch.argmax(model_output).item()
            if self.verbose:
                print(f"Greedy Action: {next_state}")
        else:
            next_state = random.randint(0, self.num_states - 1)
            if self.verbose:
                print(f"Random Action: {next_state}")
        logger.logger.log_action(self.world.get_current_time(), next_state, self.intersection.id)
        return next_state
    
    def get_current_snapshot(self):
        time_since_last_change: float = self.world.get_current_time() - self.state_start_time
        extra_data = [time_since_last_change, self.state]
        return torch.tensor([s.get_data() for s in self.world.sensors] + extra_data).float()

    def get_environment_state(self):
        """
        In the future, will need to add more to state (time since last light change, time of day, etc)
        """
        logger.logger.logSnapshots(self.get_current_snapshot())
        self.snapshots.append(self.get_current_snapshot())
        self.snapshots = self.snapshots[1:]
        env_state = torch.hstack(self.snapshots)
        if self.verbose:
            print(f"Env State: {env_state}")
        return env_state

    def control(self) -> None:
        environment_state = self.get_environment_state()
        if self.in_termination:
            if self.is_state_finished():
                self.start_next_state()
        else:
            if self.world.get_current_time() - self.state_start_time > self.min_wait_time:
                self.next_state = self.get_action(environment_state)
                if self.next_state != self.state:
                    self.in_termination = True
                    for l in self.lights[self.state]:
                        l.green_to_yellow(self.world.get_current_time())
