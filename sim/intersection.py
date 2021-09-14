from consts import *
from street import Street
from trafficlight import TrafficLight
from camera import Camera
from typing import Tuple, List
from path import Path

class Intersection:
    def __init__(self,
                 world,
                 streets, # in a clockwise order
                 paths_to_connect, # triples, incoming, outgoing, movementOption
                 ):

        self.world = world
        self.streets = streets
        self.paths = []
        self._populate_paths()
        self.paths_to_connect: List[Tuple[Path, Path, MovementOptions]] = paths_to_connect
        for s in self.streets:
            # TODO: make the intersections a heap and maintain sortedness when adding new intersections
            s.intersections.append(self)
        self.traffic_lights = {}
        self._create_traffic_lights() # TODO
        self.sub_paths = []
        self._create_paths_in_intersection()
        self._determine_boundaries()

    def _populate_paths(self):
        for street in self.streets:
            self.paths.extend(street.paths)

    def _determine_boundaries(self):
        # TODO(rajatmittal): how to determine boundaries
        self.left_boundary = min([street.min for street in self.streets
                                  if Direction.is_north_south(street.direction)])
        self.right_boundary = max([street.max for street in self.streets
                                   if Direction.is_north_south(street.direction)])
        self.lower_boundary = min([street.min for street in self.streets
                                  if not Direction.is_north_south(street.direction)])
        self.upper_boundary = max([street.max for street in self.streets
                                  if not Direction.is_north_south(street.direction)])

    def _create_paths_in_intersection(self):
        for (inbound, outbound, moveOp) in self.paths_to_connect:
            inboundEnd = inbound.end
            outboundStart = outbound.start
            subPath = Path() #TODO(rajatmittal): Hey Rajat
            inbound.add_connecting_path(subPath)
            subPath.add_connecting_path(outbound)
            # get traffic light corresponding to this path movement
            street = inbound.street
            inbound.add_traffic_light(self.traffic_lights[(street, moveOp)], moveOp)

    def _create_traffic_lights(self):
        for street in self.streets:
            self.traffic_lights[(street, MovementOptions.left)] = TrafficLight(MovementOptions.left, street.direction, self, sensor=Camera(range=30.0))
            self.traffic_lights[(street, MovementOptions.through)] = TrafficLight(MovementOptions.through, street.direction, self, sensor=Camera(range=30.0))
            self.traffic_lights[(street, MovementOptions.right)] = TrafficLight(MovementOptions.right, street.direction, self, sensor=Camera(range=30.0))
