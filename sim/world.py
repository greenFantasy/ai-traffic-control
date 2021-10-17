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
import copy

class World:
    def __init__(self):
        self.streets: List[Street] = []
        self.time: float = 0.0
        self.time_step: float = 0.1
        self.vehicles = []
        self.sensors = []
        self.traffic_lights: List[TrafficLight] = []
        self.controllers: List[Controller] = []
        logger.init(self, enable=True)

    def get_objects(self):
        objects = []
        for a in [a for a in self.__dict__.keys() if a[0] != " "]:
            if type(self.__dict__[a]) in [Street, Intersection]:
                objects.append(self.__dict__[a])
        return objects

    def add_vehicle_to_path(self, path: Path, id: str):
        car = Car(path.start, 15, 6, 5, id = id) # TODO: set the size dynamically as a parameter
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

    def log_world(self):
        logger.logger.logSaveWorld(self)

    # def build_path_w_left_turn(self, parametrization: Parametrization, width, sensors=None) -> List[Path]:
    #     commonPara = copy.deepcopy(parametrization)
    #     currentPara = copy.deepcopy(parametrization)
    #     commonPath = Path(parametrization, width, sensors)


class SimpleIntersectionWorld(World):
    def __init__(self):
        super().__init__()
        self.inner_north_lane_i = Path(LinearParam((6, -100), (6, -24)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_i = Path(LinearParam((18, -100), (18, -24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("0", [self.inner_north_lane_i, self.outer_north_lane_i]))
        self.inner_north_lane_o = Path(LinearParam((6, 24), (6, 100)), width = STANDARD_LANE_WIDTH)# Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("1", [self.inner_north_lane_o, self.outer_north_lane_o]))

        self.inner_south_lane_i = Path(LinearParam((-6, 100), (-6, 24)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_i = Path(LinearParam((-18, 100), (-18, 24)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("2", [self.inner_south_lane_i, self.outer_south_lane_i]))
        self.inner_south_lane_o = Path(LinearParam((-6, -24), (-6, -100)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_o = Path(LinearParam((-18, -24), (-18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("3", [self.inner_south_lane_o, self.outer_south_lane_o]))

        self.inner_east_lane_i = Path(LinearParam((-100, -6), (-24, -6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_i = Path(LinearParam((-100, -18), (-24, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("4", [self.inner_east_lane_i, self.outer_east_lane_i]))
        self.inner_east_lane_o = Path(LinearParam((24, -6), (100, -6)), width = STANDARD_LANE_WIDTH) # Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane_o = Path(LinearParam((24, -18), (100, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("5", [self.inner_east_lane_o, self.outer_east_lane_o]))

        self.inner_west_lane_i = Path(LinearParam((100, 6), (24, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_i = Path(LinearParam((100, 18), (24, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("6", [self.inner_west_lane_i, self.outer_west_lane_i]))
        self.inner_west_lane_o = Path(LinearParam((-24, 6), (-100, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("7", [self.inner_west_lane_o, self.outer_west_lane_o]))

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
        self.log_world()

class DedicatedLeftTurnIntersectionWorld(World):
    def __init__(self):
        super().__init__()
        self.outer_north_lane_i_common = Path(LinearParam((18, -100), (18, -44)), width = STANDARD_LANE_WIDTH)
        self.outer_north_lane_i_left = Path(LinearParam((18, -44), (6, -24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_north_lane_i_straight = Path(LinearParam((18, -44), (18, -24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_north_lane_i_common.add_connecting_path(self.outer_north_lane_i_left, MovementOptions.left)
        self.outer_north_lane_i_common.add_connecting_path(self.outer_north_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("0", [self.outer_north_lane_i_common, self.outer_north_lane_i_left, self.outer_north_lane_i_straight]))
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("1", [self.outer_north_lane_o]))

        self.outer_south_lane_i_common = Path(LinearParam((-18, 100), (-18, 44)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_i_left = Path(LinearParam((-18, 44), (-6, 24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_south_lane_i_straight = Path(LinearParam((-18, 44), (-18, 24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_south_lane_i_common.add_connecting_path(self.outer_south_lane_i_left, MovementOptions.left)
        self.outer_south_lane_i_common.add_connecting_path(self.outer_south_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("2", [self.outer_south_lane_i_common, self.outer_south_lane_i_left, self.outer_south_lane_i_straight]))
        self.outer_south_lane_o = Path(LinearParam((-18, -24), (-18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("3", [self.outer_south_lane_o]))

        self.outer_east_lane_i_common = Path(LinearParam((-100, -18), (-44, -18)), width = STANDARD_LANE_WIDTH)
        self.outer_east_lane_i_left = Path(LinearParam((-44, -18), (-24, -6)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_east_lane_i_straight = Path(LinearParam((-44, -18), (-24, -18)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_east_lane_i_common.add_connecting_path(self.outer_east_lane_i_left, MovementOptions.left)
        self.outer_east_lane_i_common.add_connecting_path(self.outer_east_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("4", [self.outer_east_lane_i_common, self.outer_east_lane_i_left, self.outer_east_lane_i_straight]))
        self.outer_east_lane_o = Path(LinearParam((24, -18), (100, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("5", [self.outer_east_lane_o]))

        self.outer_west_lane_i_common = Path(LinearParam((100, 18), (44, 18)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_i_left = Path(LinearParam((44, 18), (24, 6)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_west_lane_i_straight = Path(LinearParam((44, 18), (24, 18)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_west_lane_i_common.add_connecting_path(self.outer_west_lane_i_left, MovementOptions.left)
        self.outer_west_lane_i_common.add_connecting_path(self.outer_west_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("6", [self.outer_west_lane_i_common, self.outer_west_lane_i_left, self.outer_west_lane_i_straight]))
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("7", [self.outer_west_lane_o]))

        self.paths_to_connect = [(self.outer_north_lane_i_straight, self.outer_north_lane_o, MovementOptions.through),
                                (self.outer_north_lane_i_left, self.outer_west_lane_o, MovementOptions.left),
                                (self.outer_north_lane_i_straight, self.outer_east_lane_o, MovementOptions.right),
                                (self.outer_south_lane_i_straight, self.outer_south_lane_o, MovementOptions.through),
                                (self.outer_south_lane_i_left, self.outer_east_lane_o, MovementOptions.left),
                                (self.outer_south_lane_i_straight, self.outer_west_lane_o, MovementOptions.right),
                                (self.outer_west_lane_i_straight, self.outer_west_lane_o, MovementOptions.through),
                                (self.outer_west_lane_i_left, self.outer_south_lane_o, MovementOptions.left),
                                (self.outer_west_lane_i_straight, self.outer_north_lane_o, MovementOptions.right),
                                (self.outer_east_lane_i_straight, self.outer_east_lane_o, MovementOptions.through),
                                (self.outer_east_lane_i_left, self.outer_north_lane_o, MovementOptions.left),
                                (self.outer_east_lane_i_straight, self.outer_south_lane_o, MovementOptions.right),]

        self.intersection: Intersection = Intersection(self, self.streets, self.paths_to_connect)
        self.traffic_lights.extend(list(self.intersection.traffic_lights.values()))
        self.controllers.append(Controller(self, self.intersection, [20.] * 4))

        for s in self.streets:
            for p in s.paths:
                if len(p.connecting_paths) > 0: # only add sensors for incoming paths
                    #p.add_sensor() # TODO(rajatmittal): add_sensor requires paths to be longer than 40 feet
                    #self.sensors.extend(p.sensors)
                    pass
        self.log_world()
