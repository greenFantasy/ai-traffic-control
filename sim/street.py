from consts import *
from typing import List
from path import Path

class Street:
    def __init__(self, id: str, paths: List[Path]):
        ## TODO: Should we create the paths in the init?
        self.min = None #TODO(rajatmittal): Do we need these params
        self.max = None
        self.id = id
        self.paths = paths
        for p in self.paths:
            p.street = self
        self.intersections = []

        assert self.id, "Cannot set street id to None or empty string, otherwise path ids for paths on street will also fail."

    def __repr__(self):
        return f"Street with id {self.id}"
