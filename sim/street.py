from consts import *
from typing import List
from path import Path

class Street:
    def __init__(self, paths: List[Path]):
        ## TODO: Should we create the paths in the init?
        self.min = None #TODO(rajatmittal): Do we need these params
        self.max = None
        self.paths = paths
        for p in self.paths:
            p.street = self
        self.intersections = []
