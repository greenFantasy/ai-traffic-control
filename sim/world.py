from posixpath import split
from consts import *
from street import Street
from intersection import Intersection
from trafficlight import TrafficLight
from controller import Controller
from controller import RLController
from car import Car
from path import Path
from typing import List
from parametrization import *
import logger
import copy
import sys
import os

RL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../RL")
MODEL_FILE = "model.pt"

sys.path.append(RL_DIR)
sys.path.append('../data')

from modelcreator import StateActionNetwork

class World:
    def __init__(self, dataFolder=''):
        self.streets: List[Street] = []
        self.time: float = 0.0
        self.time_step: float = 0.1
        self.vehicles = []
        self.sensors = []
        self.traffic_lights: List[TrafficLight] = []
        self.controllers: List[Controller] = []
        self.car_id_counter: int = 0
        self.generator = None
        self.spawnable_paths = []
        self.ended: bool = False # True when the simulation is complete, set to True in the close() function
        logger.init(self, enable=True, dataFolder=dataFolder)
        self.setup_streets()
        self.set_path_ids()
        self.setup_intersections()
        self.setup_sensors()
        self.set_spawnable_paths()
        self.log_world()

    def close(self):
        # Close world
        self.ended = True
        for v in self.vehicles:
            if v.wait_time_data: # Is the vehicle in an intersection?
                v.leaving_intersection(self)
        logger.logger.close()
        
    def set_spawnable_paths(self):
        for s in self.streets:
            for p in s.paths:
                if p.spawnable:
                    self.spawnable_paths.append(p)
    
    def add_generator(self, generator) -> None:
        self.generator = generator

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

    def add_vehicle_to_path(self, path: Path, plan: List[MovementOptions], id: str = None):
        self.car_id_counter += 1
        if not id:
            id = f"car{self.car_id_counter}"
        car = Car(path.start, 15, 6, 5, id = id) # TODO: set the size dynamically as a parameter
        result = path.add_vehicle(car, plan, spawn=True)
        if result:
            self.vehicles.append(car)
            return car

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
            tl.check_yellow_to_red(self.get_current_time())
        if self.time % 2 == 0:
            for c in self.controllers:
                c.control()
        if self.generator:
            self.generator.generate() # Add cars to screen according to generator
        logger.logger.logVehicleMovement(self.vehicles)

    def get_current_time(self):
        return self.time

    def fix_time(self):
        self.time = round(self.time, 1) # int(round(self.time / self.time_step)) * self.time_step

    def log_world(self):
        logger.logger.logSaveWorld(self)
    
    def setup_streets(self):
        raise NotImplementedError

    def setup_intersections(self):
        raise NotImplementedError

    def setup_sensors(self):
        raise NotImplementedError

    # def build_path_w_left_turn(self, parametrization: Parametrization, width, sensors=None) -> List[Path]:
    #     commonPara = copy.deepcopy(parametrization)
    #     currentPara = copy.deepcopy(parametrization)
    #     commonPath = Path(parametrization, width, sensors)


class SimpleIntersectionWorld(World):
    def __init__(self, dataFolder=''):
        super().__init__(dataFolder)
        self.controllers.append(RLController(self, self.intersection, num_snapshots=5, greedy_prob=0.8))
        model = torch.load(os.path.join(RL_DIR, MODEL_FILE))
        self.controllers[0].set_model(model)
        
    
    def setup_streets(self):
        self.inner_north_lane_i = Path(LinearParam((6, -100), (6, -24)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.outer_north_lane_i = Path(LinearParam((18, -100), (18, -24)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.streets.append(Street("north_incoming", [self.inner_north_lane_i, self.outer_north_lane_i]))
        self.inner_north_lane_o = Path(LinearParam((6, 24), (6, 100)), width = STANDARD_LANE_WIDTH)
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("north_outgoing", [self.inner_north_lane_o, self.outer_north_lane_o]))

        self.inner_south_lane_i = Path(LinearParam((-6, 100), (-6, 24)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.outer_south_lane_i = Path(LinearParam((-18, 100), (-18, 24)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.streets.append(Street("south_incoming", [self.inner_south_lane_i, self.outer_south_lane_i]))
        self.inner_south_lane_o = Path(LinearParam((-6, -24), (-6, -100)), width = STANDARD_LANE_WIDTH)
        self.outer_south_lane_o = Path(LinearParam((-18, -24), (-18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("south_outgoing", [self.inner_south_lane_o, self.outer_south_lane_o]))

        self.inner_east_lane_i = Path(LinearParam((-100, -6), (-24, -6)), width = STANDARD_LANE_WIDTH, spawnable=True) 
        self.outer_east_lane_i = Path(LinearParam((-100, -18), (-24, -18)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.streets.append(Street("east_incoming", [self.inner_east_lane_i, self.outer_east_lane_i]))
        self.inner_east_lane_o = Path(LinearParam((24, -6), (100, -6)), width = STANDARD_LANE_WIDTH) 
        self.outer_east_lane_o = Path(LinearParam((24, -18), (100, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("east_outgoing", [self.inner_east_lane_o, self.outer_east_lane_o]))

        self.inner_west_lane_i = Path(LinearParam((100, 6), (24, 6)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.outer_west_lane_i = Path(LinearParam((100, 18), (24, 18)), width = STANDARD_LANE_WIDTH, spawnable=True)
        self.streets.append(Street("west_incoming", [self.inner_west_lane_i, self.outer_west_lane_i]))
        self.inner_west_lane_o = Path(LinearParam((-24, 6), (-100, 6)), width = STANDARD_LANE_WIDTH)
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("west_outgoing", [self.inner_west_lane_o, self.outer_west_lane_o]))
    
    def setup_intersections(self):
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

        self.intersection: Intersection = Intersection(self.streets, self.paths_to_connect)
        self.traffic_lights.extend(list(self.intersection.traffic_lights.values()))
    
    def setup_sensors(self):
        for s in self.streets:
            for p in s.paths:
                if len(p.connecting_paths) > 0: # only add sensors for incoming paths
                    p.add_sensor()
                    self.sensors.extend(p.sensors)

class DedicatedLeftTurnIntersectionWorld(World):
    def __init__(self, greedy_prob, split_times=[20.] * 4, dataFolder='', rl=True):
        super().__init__(dataFolder)
        if rl:
            self.controllers.append(RLController(self, self.intersection, num_snapshots=20, greedy_prob=greedy_prob))
            model = torch.load(os.path.join(RL_DIR, MODEL_FILE))
            self.controllers[0].set_model(model)
        else:
            self.controllers.append(Controller(self, self.intersection, split_times))
    
    def setup_streets(self):
        self.outer_north_lane_i_common = Path(LinearParam((18, -100), (18, -44)), width = STANDARD_LANE_WIDTH, spawnable=True, sensor=[50, 10])
        self.outer_north_lane_i_left = Path(LinearParam((18, -44), (6, -24)), width = STANDARD_LANE_WIDTH, aux_path=True, sensor=[10, 10])
        self.outer_north_lane_i_straight = Path(LinearParam((18, -44), (18, -24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_north_lane_i_common.add_connecting_path(self.outer_north_lane_i_left, MovementOptions.left)
        self.outer_north_lane_i_common.add_connecting_path(self.outer_north_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("0", [self.outer_north_lane_i_common, self.outer_north_lane_i_left, self.outer_north_lane_i_straight]))
        self.outer_north_lane_o = Path(LinearParam((18, 24), (18, 100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("1", [self.outer_north_lane_o]))

        self.outer_south_lane_i_common = Path(LinearParam((-18, 100), (-18, 44)), width = STANDARD_LANE_WIDTH, spawnable=True, sensor=[50, 10])
        self.outer_south_lane_i_left = Path(LinearParam((-18, 44), (-6, 24)), width = STANDARD_LANE_WIDTH, aux_path=True, sensor=[10, 10])
        self.outer_south_lane_i_straight = Path(LinearParam((-18, 44), (-18, 24)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_south_lane_i_common.add_connecting_path(self.outer_south_lane_i_left, MovementOptions.left)
        self.outer_south_lane_i_common.add_connecting_path(self.outer_south_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("2", [self.outer_south_lane_i_common, self.outer_south_lane_i_left, self.outer_south_lane_i_straight]))
        self.outer_south_lane_o = Path(LinearParam((-18, -24), (-18, -100)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("3", [self.outer_south_lane_o]))

        self.outer_east_lane_i_common = Path(LinearParam((-100, -18), (-44, -18)), width = STANDARD_LANE_WIDTH, spawnable=True, sensor=[50, 10])
        self.outer_east_lane_i_left = Path(LinearParam((-44, -18), (-24, -6)), width = STANDARD_LANE_WIDTH, aux_path=True, sensor=[10, 10])
        self.outer_east_lane_i_straight = Path(LinearParam((-44, -18), (-24, -18)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_east_lane_i_common.add_connecting_path(self.outer_east_lane_i_left, MovementOptions.left)
        self.outer_east_lane_i_common.add_connecting_path(self.outer_east_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("4", [self.outer_east_lane_i_common, self.outer_east_lane_i_left, self.outer_east_lane_i_straight]))
        self.outer_east_lane_o = Path(LinearParam((24, -18), (100, -18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("5", [self.outer_east_lane_o]))

        self.outer_west_lane_i_common = Path(LinearParam((100, 18), (44, 18)), width = STANDARD_LANE_WIDTH, spawnable=True, sensor=[50, 10])
        self.outer_west_lane_i_left = Path(LinearParam((44, 18), (24, 6)), width = STANDARD_LANE_WIDTH, aux_path=True, sensor=[10, 10])
        self.outer_west_lane_i_straight = Path(LinearParam((44, 18), (24, 18)), width = STANDARD_LANE_WIDTH, aux_path=True)
        self.outer_west_lane_i_common.add_connecting_path(self.outer_west_lane_i_left, MovementOptions.left)
        self.outer_west_lane_i_common.add_connecting_path(self.outer_west_lane_i_straight, MovementOptions.through)
        self.streets.append(Street("6", [self.outer_west_lane_i_common, self.outer_west_lane_i_left, self.outer_west_lane_i_straight]))
        self.outer_west_lane_o = Path(LinearParam((-24, 18), (-100, 18)), width = STANDARD_LANE_WIDTH)
        self.streets.append(Street("7", [self.outer_west_lane_o]))

    def setup_intersections(self):
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

        self.intersection: Intersection = Intersection(self.streets, self.paths_to_connect, id='1')
        self.traffic_lights.extend(list(self.intersection.traffic_lights.values()))
        self.intersections = [self.intersection]

    def setup_sensors(self):
        for s in self.streets:
            for p in s.paths:
                self.sensors.extend(p.sensors)
        # for s in self.streets:
        #     for p in s.paths:
        #         if p.spawnable:
        #             # add sensor 50 feet back
        #         elif p