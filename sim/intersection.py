from consts import *
from street import Street
from trafficlight import TrafficLight
from typing import Tuple, List
from path import Path
from parametrization import *

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
        pass
        # self.left_boundary = min([street.min for street in self.streets
        #                           if Direction.is_north_south(street.direction)])
        # self.right_boundary = max([street.max for street in self.streets
        #                            if Direction.is_north_south(street.direction)])
        # self.lower_boundary = min([street.min for street in self.streets
        #                           if not Direction.is_north_south(street.direction)])
        # self.upper_boundary = max([street.max for street in self.streets
        #                           if not Direction.is_north_south(street.direction)])

    def _create_paths_in_intersection(self):
        for (inbound, outbound, moveOp) in self.paths_to_connect:
            inboundEnd = inbound.end
            outboundStart = outbound.start
            subPath = Path(parametrization = LinearParam(inboundEnd, outboundStart), width = STANDARD_LANE_WIDTH)
            inbound.add_connecting_path(subPath, moveOp)
            subPath.add_connecting_path(outbound, MovementOptions.through)
            # get traffic light corresponding to this path movement
            street = inbound.street
            inbound.add_traffic_light(self.traffic_lights[(street.id, moveOp)], moveOp)

    def _create_traffic_lights(self):
        for street in self.streets:
            # TODO: Includes outbound streets, which we don't want
            self.traffic_lights[(street.id, MovementOptions.left)] = TrafficLight(MovementOptions.left, street.id, self, traffic_light_id="Left_"+street.id)
            self.traffic_lights[(street.id, MovementOptions.through)] = TrafficLight(MovementOptions.through, street.id, self, traffic_light_id="Through_"+street.id)
            self.traffic_lights[(street.id, MovementOptions.right)] = TrafficLight(MovementOptions.right, street.id, self, traffic_light_id="Right_"+street.id)
