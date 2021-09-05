from consts import *
from street import Street
from trafficlight import TrafficLight

class Intersection:
    def __init__(self,
                 north_street: Street = None,
                 south_street: Street = None,
                 east_street: Street = None,
                 west_street: Street = None):

        self.street_dict = {}
        self.street_dict[Direction.north] = self.north_street = north_street
        self.street_dict[Direction.south] = self.south_street = south_street
        self.street_dict[Direction.east] = self.east_street = east_street
        self.street_dict[Direction.west] = self.west_street = west_street
        self.streets = [s for s in self.street_dict if s]
        for s in self.streets:
            # TODO: make the intersections a heap and maintain sortedness when adding new intersections
            s.intersections.append(self)

        self._determine_boundaries()
        self._create_traffic_lights() # TODO

        # Must be at least one street going north-south and one street going east-west
        assert((north_street or south_street) and (east_street or west_street))

    def _determine_boundaries(self):
        self.left_boundary = min([street.min for street in self.streets
                                  if Direction.is_north_south(street.direction)])
        self.right_boundary = max([street.max for street in self.streets
                                   if Direction.is_north_south(street.direction)])
        self.lower_boundary = min([street.min for street in self.streets
                                  if not Direction.is_north_south(street.direction)])
        self.upper_boundary = max([street.max for street in self.streets
                                  if not Direction.is_north_south(street.direction)])

    def _create_traffic_lights(self):
        self.traffic_lights = {}
        for street in self.streets:
            self.traffic_lights[(street.direction, MovementOptions.left)] = TrafficLight(MovementOptions.left, street.direction, self)
            self.traffic_lights[(street.direction, MovementOptions.through)] = TrafficLight(MovementOptions.through, street.direction, self)
            self.traffic_lights[(street.direction, MovementOptions.right)] = TrafficLight(MovementOptions.right, street.direction, self)
