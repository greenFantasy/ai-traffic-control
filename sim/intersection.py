from consts import *
from street import Street
from trafficlight import TrafficLight
from typing import Tuple, List, Optional
from path import Path
from parametrization import *

global id_counter 
id_counter = 1

class Intersection:
    def __init__(self,
                 world,
                 streets, # in a clockwise order
                 paths_to_connect, # triples, incoming, outgoing, movementOption
                 id: Optional[int] = None # identifier for intersection must be int or None
                 ):
        self.world = world
        self.streets = streets
        self.paths = []
        self.set_id(id)
        self._populate_paths()
        self.paths_to_connect: List[Tuple[Path, Path, MovementOptions]] = paths_to_connect
        self.incoming_paths = self._get_incoming_paths()
        for s in self.streets:
            # TODO: make the intersections a heap and maintain sortedness when adding new intersections
            s.intersections.append(self)
        self.traffic_lights = {}
        self._create_traffic_lights() # TODO
        self.sub_paths = []
        self._create_paths_in_intersection()
        self._determine_boundaries()

    def set_id(self, id): # Every time a new intersection is created, it is given an id that is one larger than the last intersection
        self.id = id
        if id is None:
            global id_counter
            self.id = id_counter
            id_counter += 1

    def _get_incoming_paths(self):
        # TODO (rajatmittal): Document assumption that incomcing path is in path_to_connect
        incoming_paths = []
        for p in self.paths_to_connect:
            if p[0] not in incoming_paths:
                incoming_paths.append(p)
        return incoming_paths

    def get_approaching_vehicles(self):
        vehicles = []
        for path in self.incoming_paths:
            vehicles.extend(path.get_vehicles(self.parametrization.max_pos - 50, self.parametrization.max_pos))
        return vehicles

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
            subPath = Path(parametrization = LinearParam(inboundEnd, outboundStart), width = STANDARD_LANE_WIDTH, speed_limit=20)
            subPath.set_id(f"{moveOp}_CONNECTING--{inbound.id}--{outbound.id}")
            self.sub_paths.append(subPath)
            inbound.add_connecting_path(subPath, moveOp)
            subPath.add_connecting_path(outbound, MovementOptions.through)
            self.sub_paths.append(subPath)
            # get traffic light corresponding to this path movement
            street = inbound.street
            inbound.add_traffic_light(self.traffic_lights[(street.id, moveOp)], moveOp)

    def _create_traffic_lights(self):
        for street in self.streets:
            # TODO: Includes outbound streets, which we don't want
            self.traffic_lights[(street.id, MovementOptions.left)] = TrafficLight(MovementOptions.left, street.id, self, traffic_light_id="Left_"+street.id)
            self.traffic_lights[(street.id, MovementOptions.through)] = TrafficLight(MovementOptions.through, street.id, self, traffic_light_id="Through_"+street.id)
            self.traffic_lights[(street.id, MovementOptions.right)] = TrafficLight(MovementOptions.right, street.id, self, traffic_light_id="Right_"+street.id)
