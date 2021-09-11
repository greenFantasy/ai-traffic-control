from consts import *

class Path:
    def __init__(self, parametrization: Parametrization):
        self.parametrization = parametrization
        self.start = self.parametrization.get_pos(0) # Starting coordinates
        self.end = self.parametrization.get_pos(self.parametrization.max_p) # Ending coordinates
        self.vehicles = [] # TODO: will vehicles list contain tuple elements like before? If so, first element should be p-value, and second element shoulld be vehicle

    def add_connecting_path(self, path)
        # TODO: connect path and self
        pass

    def add_traffic_light(self, traffic_light, pos):
        # TODO: add traffic light to a position along this path
        pass
