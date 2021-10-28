from trafficlight import TrafficLight
from intersection import Intersection
from consts import *
from typing import List
import torch

class Controller:

    def __init__(self, world, intersection, split_times):
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
                self.next_state = (self.state + 1) % self.num_states

class RLController(Controller):

    def __init__(self, world, intersection, num_snapshots: int, reward_window: float):
        super().__init__(world, intersection, [])

        self.min_wait_time = 5.0

        self.mode='eval' # Can be train or eval
        self.reward_prep = [] # list of tuples, (time, reward)
        self.previous_actions = [] # list of (time, state, action) or (time, state, action, next_state)
        self.sars_to_save = [] # list of (state, action, reward, next_state) tuples

        # State calculation
        self.total_snapshots: int = num_snapshots
        self.snapshots: List[torch.tensor] = [self.get_current_snapshot() for _ in range(num_snapshots)]

        # Reward Calculation
        self.reward_window: float = reward_window # number of seconds after action which we use to compute the reward

    def set_model(self, model):
        self.model = model

    def get_action(self, env_state):
        input = env_state.unsqueeze(0)
        return int(torch.argmax(self.model.forward(input).squeeze(0)))
    
    def get_current_snapshot(self):
        return torch.tensor([s.get_data() for s in self.world.sensors]).float()

    def get_environment_state(self):
        """
        In the future, will need to add more to state (time since last light change, time of day, etc)
        """
        self.snapshots.append(self.get_current_snapshot())
        self.snapshots = self.snapshots[1:]
        return torch.hstack(self.snapshots)

    def prepare_reward(self):
        """
        Avg wait time for cars WHILE they are at the intersection during the n second window of this action.
        As such, max wait time per car will be n seconds, if the reward period is n seconds.
        Compute distance2nearestintersection to compute rewards outside of simulation
        """
        self.reward_prep.append((self.world.get_current_time(), set(self.intersection.get_approaching_vehicle_ids())))

    def compute_reward(self, action_time):
        wait_times = []
        incoming_time: dict[str][float] = {}
        curr_cars = set()
        for time, vehicles in self.reward_prep:
            if rp[0] < action_time:
                continue
            new_curr_cars = curr_cars
            for v in curr_cars:
                if v not in rp[1]:
                    incoming_time[v] - rp[0]
                else:
                    new_curr_cars.append(v)

    def update_saved_sars(self):
        # For all tuples in previous_actions with a next_state and a computable reward remove from previous actions
        if len(self.previous_actions[-1]) == 4: # contains (time, env_state, action, next_env_state)
            if reward_prep[-1][0] >= self.reward_window + self.previous_actions[-1][0]:
                # Enough time has passed so we can compute the reward
                pass

    def control(self) -> None:
        # self.prepare_reward() # appends to rewards
        # self.update_saved_sars() # removes action from previous_actions and puts it into sars_to_save with the next_state and reward both updated
        environment_state = self.get_environment_state()
        if self.in_termination:
            if self.is_state_finished():
                self.start_next_state()
        else:
            if self.world.get_current_time() - self.state_start_time > self.min_wait_time:
                # if self.previous_actions:
                #    self.previous_actions[0] = tuple(list(self.previous_actions[0]) + [environment_state])
                self.next_state = self.get_action(environment_state)
                # self.previous_actions = [(self.world.get_current_time(), environment_state, self.next_states)] + self.previous_actions
                if self.next_state != self.state:
                    self.in_termination = True
                    for l in self.lights[self.state]:
                        l.green_to_yellow()
