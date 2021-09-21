from consts import *
from street import Street
from intersection import Intersection
from trafficlight import TrafficLight
from car import Car
from path import Path
from parametrization import *
import logger

class World:
    def __init__(self):
        self.streets = []
        self.time = 0
        self.time_step = .1
        self.vehicles = []
        self.sensors = []
        logger.init(self)

    def get_objects(self):
        objects = []
        for a in [a for a in self.__dict__.keys() if a[0] != " "]:
            if type(self.__dict__[a]) in [Street, Lane, Intersection]:
                objects.append(self.__dict__[a])
        return objects

    def add_vehicle_to_path(self, path: Path):
        car = Car(path.start, 15, 6, 5, id = "car1") # TODO: set the size dynamically as a parameter
        path.add_vehicle(car)
        self.vehicles.append(car)

    def play(self):
        for v in self.vehicles:
            v.move(self.time_step)
        self.time += self.time_step

    def get_current_time(self):
        return self.time

class SimpleIntersectionWorld(World):
    def __init__(self):
        super().__init__()
        self.inner_north_lane_i = Path(LinearParam((6, -100), (6, -24)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_i = Path(LinearParam((18, -100), (18, -24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(0, [self.inner_north_lane_i, self.outer_north_lane_i]))
        self.inner_north_lane_o = Path(LinearParam((6, 24), (6, 100)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(1, [self.inner_north_lane_o, self.outer_north_lane_o]))

        self.inner_south_lane_i = Path(LinearParam((6, 100), (6, 24)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_i = Path(LinearParam((18, 100), (18, 24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(2, [self.inner_south_lane_i, self.outer_south_lane_i]))
        self.inner_south_lane_o = Path(LinearParam((6, -24), (6, -100)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_o = Path(LinearParam((18, -24), (18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(3, [self.inner_south_lane_o, self.outer_south_lane_o]))

        self.inner_east_lane_i = Path(LinearParam((-100, 6), (-24, 6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_i = Path(LinearParam((-100, 18), (-24, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(4, [self.inner_east_lane_i, self.outer_east_lane_i]))
        self.inner_east_lane_o = Path(LinearParam((24, 6), (100, 6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_o = Path(LinearParam((24, 18), (100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(5, [self.inner_east_lane_o, self.outer_east_lane_o]))

        self.inner_west_lane_i = Path(LinearParam((100, 6), (24, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_i = Path(LinearParam((100, 18), (24, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(6, [self.inner_west_lane_i, self.outer_west_lane_i]))
        self.inner_west_lane_o = Path(LinearParam((-24, 6), (-100, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street(7, [self.inner_west_lane_o, self.outer_west_lane_o]))

        for s in self.streets:
            for p in s.paths:
                if len(p.connecting_paths) > 0:
                    p.add_sensor()
                    self.sensors.extend(p.sensors)

        self.paths_to_connect = [(self.inner_north_lane_i, self.inner_north_lane_o, MovementOptions.through),
                                (self.outer_north_lane_i, self.outer_north_lane_o, MovementOptions.through),
                                (self.inner_north_lane_i, self.inner_west_lane_o, MovementOptions.left),
                                (self.outer_north_lane_i, self.outer_east_lane_o, MovementOptions.right),
                                (self.inner_south_lane_i, self.inner_south_lane_o, MovementOptions.through),
                                (self.outer_south_lane_i, self.outer_south_lane_o, MovementOptions.through),
                                (self.inner_south_lane_i, self.inner_east_lane_o, MovementOptions.left),
                                (self.outer_south_lane_i, self.outer_west_lane_o, MovementOptions.right),
                                (self.inner_west_lane_i, self.inner_west_lane_o, MovementOptions.through),
                                (self.outer_west_lane_i, self.outer_west_lane_o, MovementOptions.through),
                                (self.inner_west_lane_i, self.inner_south_lane_o, MovementOptions.left),
                                (self.outer_west_lane_i, self.outer_north_lane_o, MovementOptions.right),
                                (self.inner_east_lane_i, self.inner_east_lane_o, MovementOptions.through),
                                (self.outer_east_lane_i, self.outer_east_lane_o, MovementOptions.through),
                                (self.inner_east_lane_i, self.inner_north_lane_o, MovementOptions.left),
                                (self.outer_east_lane_i, self.outer_south_lane_o, MovementOptions.right),]

        self.intersection = Intersection(self, self.streets, self.paths_to_connect)
