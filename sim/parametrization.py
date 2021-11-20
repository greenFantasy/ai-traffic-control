from consts import *
from collections.abc import Callable
import torch

class Parametrization:
    def __init__(self,
        name: str,
        coor_func, # Callable[[float], Tuple[float, float]],
        max_pos: float,
        starting_coors: Tuple[float, float]=(0, 0),
        infinite_beginning=False
    ):

        assert(len(coor_func(0)) == 2) # coor_func must return a length 2 tuple
        self.name = name
        self.coor_func: Callable[[float], Tuple[float, float]] = coor_func
        self.max_pos: float = max_pos # cannot feed in pos > max_pos into coor_func
        self.starting_coors = starting_coors
        self.infinite_beginning = infinite_beginning

    def get_pos(self, p) -> Tuple[float, float]:
        # get position associated with p
        if p > self.max_pos:
            raise ValueError(f'p = {p} > {self.max_pos} allowed for {self.name} parametrization')

        (x, y) = self.coor_func(p)
        return (x + self.starting_coors[0], y + self.starting_coors[1])

    def get_direction_vector(self, p) -> Tuple[float, float]:
        # TODO: get direction vector associated with a specific position along the path, to determine which angle the vehicle should be facing
        pass

    def get_perp_vector(self, p) -> Tuple[float, float]:
        x, y = self.get_direction_vector(p)
        return y, -x

class LinearParam(Parametrization):
    def __init__(self, start_coor: Tuple[float, float], end_coor: Tuple[float, float], name=None):
        start_tensor, end_tensor = torch.tensor(start_coor, dtype=float), torch.tensor(end_coor, dtype=float)
        norm = torch.norm(end_tensor - start_tensor)
        self.direction_vector = (end_tensor - start_tensor) / norm
        self.x_dir = float(self.direction_vector[0])
        self.y_dir = float(self.direction_vector[1])
        #coor_func = lambda p: tuple((p * self.direction_vector).tolist())
        coor_func = lambda p: (p*self.x_dir, p*self.y_dir)
        max_pos = float(norm)
        super().__init__(name, coor_func, max_pos, start_coor)

    def get_direction_vector(self, p) -> Tuple[float, float]:
        return tuple(self.direction_vector.tolist())

class CounterClockwiseParam(Parametrization):
    def __init__(self, name, start_coor: Tuple[float, float], end_coor: Tuple[float, float], radius = None, angle = None):
        start_tensor, end_tensor = torch.tensor(start_coor), torch.tensor(end_coor)
        if radius:
            pass
        elif angle:
            pass
        else:
            raise ValueError("Either angle or radius has be to specified")
