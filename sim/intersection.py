from consts import *
from street import Street

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
        self.streets = [north_street, south_street,
                        east_street, west_street]

        self.boundaries = self._determine_boundaries() # TODO
        self.traffic_lights = self._create_traffic_lights() # TODO

        # Must be at least one street going north-south and one street going east-west
        assert((north_street or south_street) and (east_street or west_street))

    def _determine_boundaries(self):
        # TODO
        return None

    def _create_traffic_lights(self):
        # TODO
        return NOne
