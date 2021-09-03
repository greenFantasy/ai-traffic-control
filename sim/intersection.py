from consts import *
from street import Street
from trafficlight import TrafficLight

class Intersection:
    def __init__(self,
                 north_street: Street = None,
                 south_street: Street = None,
                 east_street: Street = None,
                 west_street: Street = None):

        self.north_street = north_street
        self.south_street = south_street
        self.east_street = east_street
        self.west_street = west_street
        self.streets = [s for s in [north_street, south_street,
                        east_street, west_street] if s]

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
            self.traffic_lights[(street.direction, MovementOptions.left)] = TrafficLight(set([MovementOptions.left]))
            self.traffic_lights[(street.direction, MovementOptions.through)] = TrafficLight(set([MovementOptions.through]))
            self.traffic_lights[(street.direction, MovementOptions.right)] = TrafficLight(set([MovementOptions.right]))
