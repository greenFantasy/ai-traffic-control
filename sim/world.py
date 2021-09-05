from consts import *
from street import Street
from lane import Lane
from intersection import Intersection
from trafficlight import TrafficLight

class World:
    def __init__(self):
        # TODO
        self.streets = []
        self.time = 0
        self.time_step = .1

    def get_objects(self):
        # TODO
        pass

    def get_vehicles(self):
        # TODO
        pass

    def play(self):
        ...
        self.time += self.time_step

    def get_current_time(self):
        return self.time

class SimpleIntersectionWorld(World):
    def __init__(self):
        self.inner_north_lane = Lane(Direction.north, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_north_lane = Lane(Direction.north, 1.5*STANDARD_LANE_WIDTH, STANDARD_LANE_WIDTH)

        self.inner_south_lane = Lane(Direction.south, -STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_south_lane = Lane(Direction.south, -1.5*STANDARD_LANE_WIDTH, STANDARD_LANE_WIDTH)

        self.inner_west_lane = Lane(Direction.west, STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_west_lane = Lane(Direction.west, 1.5*STANDARD_LANE_WIDTH, STANDARD_LANE_WIDTH)

        self.inner_east_lane = Lane(Direction.east, -STANDARD_LANE_WIDTH/2, STANDARD_LANE_WIDTH)
        self.outer_east_lane = Lane(Direction.east, -1.5*STANDARD_LANE_WIDTH, STANDARD_LANE_WIDTH)

        self.north_street = Street(Direction.north, [self.inner_north_lane, self.outer_north_lane])
        self.south_street = Street(Direction.south, [self.inner_south_lane, self.outer_south_lane])
        self.west_street = Street(Direction.west, [self.inner_west_lane, self.outer_west_lane])
        self.east_street = Street(Direction.east, [self.inner_east_lane, self.outer_east_lane])

        self.streets = [self.north_street, self.south_street, self.west_street, self.east_street]

        self.intersection = Intersection(world,
                                         north_street=self.north_street,
                                         south_street=self.south_street,
                                         west_street=self.west_street,
                                         east_street=self.east_street)
