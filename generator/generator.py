"""
Cars should be generated in the world in a controlled fashion when we're evaluating
the performance of our signal control algorithms. By controlled, we don't necessarily 
mean deterministic, but controlled means making explicit the data-generating distribution
the cars are being generated from.

Car appearance distributions can either by time-dependent (probability of a car being generated on 
path a at time t_1 is not equal to probability of a car being generated on path a at time t_2).

Can feed in a seed that is used only by the generator for reproducable results in the params dictionary argument.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import random

from planner import SimplePlanner

class Generator(ABC):

    def __init__(self, world, params: Dict[str, Any]) -> None:
        self.world = world
        seed = params.get('seed', None)
        self.rand_generator = random.Random(seed)
        self.planner = SimplePlanner(world, {})
        [setattr(self, k, v) for k, v in params.items()]
        
    @abstractmethod
    def generate(self) -> None:
        """
        Adds car to the world according to the specified distribution. Called at each time-step
        from the World class.
        (Calls world.add_vehicle_to_path() function to add a new vehicle to a specific path.)
        """
        pass
    
class SimpleGenerator(Generator):
    """
    Generates a car on a path with probability p at each time step. Modifying the time step will
    significantly alter the amount of cars produced (that is, it'll completely change the generating
    probability distribution). Possible TO DO (rajatmittal): Look into making the class so that it 
    behaves *approximately* the same under any time step. From Poisson distributions, should be 
    able to divide probability by change in magnitude of time step to get new probability.
    """
    def __init__(self, world, params) -> None:
        super().__init__(world, params)
        assert 1 >= self.p >= 0

    def generate(self, verbose=False) -> None:
        for path in self.world.spawnable_paths:
            if self.rand_generator.random() < self.p:
                plan = self.planner.create_plan(path)
                car = self.world.add_vehicle_to_path(path, plan)
                if car and verbose:
                    print(f"Adding car to {path}")

class MarkovGenerator(Generator):
    """
    Produces more realistic car distribution than the simple generator. In particular, instead of being completely random,
    cars are more likely to follow other cars, and no cars are more likely to follow no cars. Phrased differently,
    the probability of a car being spawned on a path if a car was spawned on that path in the last second will relatively high,
    while the probability of a car being spawned on a path if a car was NOT spawned on that path in the last second will
    be relatively low. Thus, all we need to do is define a transition matrix with 4 probabilities (car -> car, car -> no car, 
    no car -> no car, no car -> car) and we can generate more realistic distributions of cars that don't just appear one 
    at a time randomly but in chains as they do in normal traffic.
    """
    def __init__(self, world, params):
        """
        params should contain car-to-car prob and no-car-to-no-car prob.
        """
        super().__init__(world, params)
        assert 1 >= self.car2car >= 0
        assert 1 >= self.nocar2nocar >= 0
        self.car_added: Dict = {} # Path -> float

    def generate(self, verbose=False) -> None:
        for path in self.world.spawnable_paths:
            time_since_last_car = self.world.get_current_time() - self.car_added.get(path, -float('inf'))
            car_prob = self.car2car if time_since_last_car <= 1 else 1 - self.nocar2nocar

            if self.rand_generator.random() < car_prob:
                plan = self.planner.create_plan(path)
                car = self.world.add_vehicle_to_path(path, plan)
                if car:
                    self.car_added[path] = self.world.get_current_time()
                    if verbose:
                        print(f"Adding car to {path}")

