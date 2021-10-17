from consts import *
from street import Street
from intersection import Intersection
from trafficlight import TrafficLight
from controller import Controller
from car import Car
from path import Path
from typing import List
from parametrization import *
import logger

class World:
    def __init__(self):
        self.streets: List[Street] = []
        self.time: float = 0.0
        self.time_step: float = 0.1
        self.vehicles = []
        self.sensors = []
        self.traffic_lights: List[TrafficLight] = []
        self.controllers: List[Controller] = []
        self.car_id_counter: int = 0
        logger.init(self, enable=True)

    def set_path_ids(self) -> None:
        """
        Sets the ids of all the paths in the world. The id is defaulted to the
        name of the variable in the world class, otherwise it's related to the
        street name.
        """
        for k, v in self.__dict__.items():
            if isinstance(v, Path):
                v.set_id(k)
        for s in self.streets:
            i = 0
            for p in s.paths:
                if not p.id:
                    p.set_id(f"{s.id}--{i}")
                    i += 1

    def get_objects(self):
        objects = []
        for a in [a for a in self.__dict__.keys() if a[0] != " "]:
            if type(self.__dict__[a]) in [Street, Intersection]:
                objects.append(self.__dict__[a])
        return objects

    def add_vehicle_to_path(self, path: Path):
        self.car_id_counter += 1
        car = Car(path.start, 15, 6, 5, id = f"car{self.car_id_counter}") # TODO: set the size dynamically as a parameter
        result = path.add_vehicle(car)
        if result:
            self.vehicles.append(car)

    def play(self):
        self.time += self.time_step
        self.fix_time()
        # Move the vehicles
        for v in self.vehicles:
            v.move(self.time_step, self)
        # Log sensor data every second
        if isclose(int(round(self.time)),self.time):
            for s in self.sensors:
                logger.logger.logSensorData(s)
        # Turn traffic lights from yellow to red as needed
        for tl in self.traffic_lights:
            tl.check_yellow_to_red()
        if self.time % 2 == 0:
            for c in self.controllers:
                c.control()
        logger.logger.logVehicleMovement(self.vehicles)

    def get_current_time(self):
        return self.time

    def fix_time(self):
        self.time = round(self.time, 1) # int(round(self.time / self.time_step)) * self.time_step

class SimpleIntersectionWorld(World):
    def __init__(self):
        super().__init__()
        self.inner_north_lane_i = Path(LinearParam((6, -100), (6, -24)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_i = Path(LinearParam((18, -100), (18, -24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("north_incoming", [self.inner_north_lane_i, self.outer_north_lane_i]))
        self.inner_north_lane_o = Path(LinearParam((6, 24), (6, 100)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("north_outgoing", [self.inner_north_lane_o, self.outer_north_lane_o]))

        self.inner_south_lane_i = Path(LinearParam((-6, 100), (-6, 24)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_i = Path(LinearParam((-18, 100), (-18, 24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("south_incoming", [self.inner_south_lane_i, self.outer_south_lane_i]))
        self.inner_south_lane_o = Path(LinearParam((-6, -24), (-6, -100)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_o = Path(LinearParam((-18, -24), (-18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("south_outgoing", [self.inner_south_lane_o, self.outer_south_lane_o]))

        self.inner_east_lane_i = Path(LinearParam((-100, -6), (-24, -6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_i = Path(LinearParam((-100, -18), (-24, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("east_incoming", [self.inner_east_lane_i, self.outer_east_lane_i]))
        self.inner_east_lane_o = Path(LinearParam((24, -6), (100, -6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_o = Path(LinearParam((24, -18), (100, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("east_outgoing", [self.inner_east_lane_o, self.outer_east_lane_o]))

        self.inner_west_lane_i = Path(LinearParam((100, 6), (24, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_i = Path(LinearParam((100, 18), (24, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("west_incoming", [self.inner_west_lane_i, self.outer_west_lane_i]))
        self.inner_west_lane_o = Path(LinearParam((-24, 6), (-100, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("west_outgoing", [self.inner_west_lane_o, self.outer_west_lane_o]))

        self.set_path_ids() # Set ids for all the paths created above.

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

        self.intersection: Intersection = Intersection(self, self.streets, self.paths_to_connect)
        self.traffic_lights.extend(list(self.intersection.traffic_lights.values()))
        self.controllers.append(Controller(self, self.intersection, [20.] * 4))

        for s in self.streets:
            for p in s.paths:
                if len(p.connecting_paths) > 0: # only add sensors for incoming paths
                    p.add_sensor()
                    self.sensors.extend(p.sensors)
