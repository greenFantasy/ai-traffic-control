from consts import *
from street import Street
from intersection import Intersection
from trafficlight import TrafficLight
from car import Car
from path import Path
from parametrization import *

class World:
    def __init__(self):
        self.streets = []
        self.time = 0
        self.time_step = .1
        self.vehicles = []

    def get_objects(self):
        objects = []
        for a in [a for a in self.__dict__.keys() if a[0] != " "]:
            if type(self.__dict__[a]) in [Street, Lane, Intersection]:
                objects.append(self.__dict__[a])
        return objects

    def add_vehicle_to_lane(self, path: Path):
        # Calculate the end of lane
        # First, get last car in lane:
        # lastCar = lane.get_vehicles()[-1] if lane.get_vehicles() else None
        # # Then, get last intersection in lane
        # street = lane.street
        # lastIntersection = street.intersections[0] # TODO actually get the last intersection once it's a heap
        # assert lastCar or lastIntersection, "Rajat help me"
        # if lane.direction == Direction.north:
        #     min = float("inf")
        #     if lastCar:
        #         if lastCar.rear_left[1]<min:
        #             min = lastCar.rear_left[1]
        #     if lastIntersection.lower_boundary<min:
        #         min = lastIntersection.lower_boundary
        # elif lane.direction == Direction.south:
        #     min = -float("inf")
        #     if lastCar:
        #         if lastCar.rear_left[1]>min:
        #             min = lastCar.rear_left[1]
        #     if lastIntersection.upper_boundary>min:
        #         min = lastIntersection.upper_boundary
        # elif lane.direction == Direction.east:
        #     min = float("inf")
        #     if lastCar:
        #         if lastCar.rear_left[0]<min:
        #             min = lastCar.rear_left[0]
        #     if lastIntersection.left_boundary<min:
        #         min = lastIntersection.left_boundary
        # elif lane.direction == Direction.west:
        #     min = -float("inf")
        #     if lastCar:
        #         if lastCar.rear_left[0]>min:
        #             min = lastCar.rear_left[0]
        #     if lastIntersection.right_boundary>min:
        #         min = lastIntersection.right_boundary
        # # TODO(sssai): center the cars in the lane
        # if lane.direction == Direction.north:
        #     rear_left = (lane.min + 2,min-30)
        # elif lane.direction == Direction.south:
        #     rear_left = (lane.max - 2,min+30)
        # elif lane.direction == Direction.east:
        #     rear_left = (min-30, lane.max - 2)
        # elif lane.direction == Direction.west:
        #     rear_left = (min+30, lane.min+2)
        car = Car(path.start, 15, 6, 5) # TODO: set the size dynamically as a parameter
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
