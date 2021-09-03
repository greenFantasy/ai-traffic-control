from consts import *
from street import Street
from lane import Lane
from intersection import Intersection
from trafficlight import TrafficLight

class World:
    def __init__(self):
        # TODO
        self.streets = []

    def get_objects(self):
        # TODO
        pass

    def get_vehicles(self):
        # TODO
        pass

class SimpleIntersectionWorld(World):
    def __init__(self):
        self.inner_north_lane = Lane(Direction.north, 1.0, 2.0)
        self.outer_north_lane = Lane(Direction.north, 3.0, 2.0)

        self.inner_south_lane = Lane(Direction.south, -1.0, 2.0)
        self.outer_south_lane = Lane(Direction.south, -3.0, 2.0)

        self.inner_west_lane = Lane(Direction.west, 1.0, 2.0)
        self.outer_west_lane = Lane(Direction.west, 3.0, 2.0)

        self.inner_east_lane = Lane(Direction.east, -1.0, 2.0)
        self.outer_east_lane = Lane(Direction.east, -3.0, 2.0)

        self.north_street = Street(Direction.north, [self.inner_north_lane, self.outer_north_lane])
        self.south_street = Street(Direction.south, [self.inner_south_lane, self.outer_south_lane])
        self.west_street = Street(Direction.west, [self.inner_west_lane, self.outer_west_lane])
        self.east_street = Street(Direction.east, [self.inner_east_lane, self.outer_east_lane])

        self.streets = [self.north_street, self.south_street, self.west_street, self.east_street]

        self.intersection = Intersection(north_street=self.north_street,
                                         south_street=self.south_street,
                                         west_street=self.west_street,
                                         east_street=self.east_street)
