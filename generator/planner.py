import random
from typing import Dict
from abc import ABC, abstractmethod

class Planner(ABC):
    def __init__(self, world, params: Dict):
        self.world = world
        seed = params.get('seed', None)
        self.rand_generator_planner = random.Random(f"planner_{seed}" if seed else None)
        [setattr(self, k, v) for k, v in params.items()]
    
    @abstractmethod
    def create_plan(self, path):
        """
        Returns a list of movement options for the car that is being added to the given path to follow.
        The car will follow this the movement option at the corresponding position in the list every time it 
        has to switch paths.
        """
        pass

class SimplePlanner(Planner):
    def create_plan(self, path):
        plan = []
        curr_path = path # Path that car is being placed on
        while len(curr_path.connecting_paths) > 0:
            idx = self.rand_generator_planner.randint(0, len(curr_path.connecting_paths) - 1)
            plan.append(list(curr_path.connecting_paths.keys())[idx])
            curr_path = curr_path.connecting_paths[plan[-1]]
        return plan