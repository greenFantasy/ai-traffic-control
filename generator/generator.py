"""
Cars should be generated in the world in a controlled fashion when we're evaluating
the performance of our signal control algorithms. By controlled, we don't necessarily 
mean deterministic, but controlled means making explicit the data-generating distribution
the cars are being generated from.

Car appearance distributions can either by time-dependent (probability of a car being generated on 
path a at time t_1 is not equal to probability of a car being generated on path a at time t_2).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import random

class Generator(ABC):

    def __init__(self, world, params: Dict[str, Any]) -> None:
        self.world = world
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

    def generate(self) -> None:
        for path in self.world.spawnable_paths:
            if random.random() < self.p:
                self.world.add_vehicle_to_path(path)
                print(f"Adding car to {path}")