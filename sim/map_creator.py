# from posixpath import split
import numpy as np

from consts import *
from street import Street
from intersection import Intersection
from trafficlight import TrafficLight
from controller import Controller
from controller import RLController
from car import Car
from path import Path
from typing import List, NamedTuple, Tuple
from parametrization import *
from collections import namedtuple
# import logger
# import copy
# import sys
# import os

def get_intersection_point(s1, e1, s2, e2) -> Tuple[float, float]:
    x1, y1 = s1
    x2, y2 = e1
    x3, y3 = s2
    x4, y4 = e2
    D = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / D
    y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / D
    return x, y

class MapStreet:
    def __init__(self, id, start, end, num_lanes):
        self.id = id
        self.start = start
        self.end = end
        self.num_lanes = num_lanes
        self.int_dict = {}
        self.int_streets = {}
        self.paths = []
    
    def add_intersection(self, intersection, location):
        self.int_dict[intersection] = location
        self.int_streets[intersection] = self.int_streets.get(intersection, [])
    
    def create_single_street(self, start, end, name, left_turn, spawnable):
        new_paths = []
        for i in range(self.num_lanes):
            full_param = LinearParam(start, end)
            common_param = LinearParam(start, full_param.get_pos(44, neg=True)) # Replace magic number with constant
            straight_param = LinearParam(full_param.get_pos(44, neg=True), full_param.get_pos(24, neg=True))
            
            common_path = Path(common_param, width = STANDARD_LANE_WIDTH, id=f"{self.id}_{name}_lane_{i}_common", spawnable=spawnable, sensor=[50, 10] if left_turn else None)
            straight_path = Path(straight_param, width = STANDARD_LANE_WIDTH, id=f"{self.id}_{name}_lane_{i}_straight", aux_path=True)
            new_paths.extend([common_path, straight_path])
            common_path.add_connecting_path(straight_path, MovementOptions.through)

            if i == 0 and left_turn: # The inner most lane has a left turn lane that stems off of it
                left_param = LinearParam(full_param.get_pos(44, neg=True), full_param.get_pos(24, neg=True))
                left_path = Path(left_param, width = STANDARD_LANE_WIDTH, id=f"{self.id}_{name}_lane_{i}_left", aux_path=True, sensor=[10, 10])
                common_path.add_connecting_path(left_path, MovementOptions.left)
                new_paths.append(left_path)
            
        self.paths.extend(new_paths)
        return Street(f"{self.id}_{name}", new_paths)

    def create_streets(self):
        start_arr = np.array(self.start)
        sorted_splits = [(None, self.start)] + sorted(self.int_dict.items(), \
            key=lambda x: np.linalg.norm(np.array(x[1]) - start_arr)) + [(None, self.end)]
        
        for idx, ((i1, start), (i2, end)) in enumerate(zip(sorted_splits[:-1], sorted_splits[1:])):
            is_end = (idx == (len(sorted_splits) - 2))
            is_beginning = (idx == 0)
            s1 = self.create_single_street(start, end, f"forward_{idx}", not is_end, is_beginning)
            s2 = self.create_single_street(end, start, f"backward_{len(sorted_splits) - 2 - idx}", not is_beginning, is_end)

            if i1:
                self.int_streets[i1].insert(1, s1)
                self.int_streets[i1].insert(2, s2)
            if i2: 
                # Order here is very specific, should not change this code without preserving order
                self.int_streets[i2].extend([s1, s2])

    def get_streets_for_intersection(self, intersection):
        return self.int_streets[intersection]

IntersectionTuple = namedtuple('IntersectionTuple', ['id', 'street1', 'street2', 'num_left_lanes'])

s_list = [
    MapStreet(id='horizontal', start=(-100, 0), end=(100, 0), num_lanes=1), 
    MapStreet(id='vertical', start=(0, -100), end=(0, 100), num_lanes=1)
    ]
s_dict = {s.id: s for s in s_list}
int_list = [IntersectionTuple(id='1', street1='horizontal', street2='vertical', num_left_lanes=1)]

for i in int_list:
    s1 = s_dict[i.street1]
    s2 = s_dict[i.street2]
    p = get_intersection_point(s1.start, s1.end, s2.start, s2.end)
    s1.add_intersection(i, p)
    s2.add_intersection(i, p)

for s in s_list:
    s.create_streets()

intersections = []
for i in int_list:
    s1 = s_dict[i.street1].get_streets_for_intersection(i)
    s2 = s_dict[i.street2].get_streets_for_intersection(i)
    paths_to_connect = [(s1[0].paths[1], s1[1].paths[0], MovementOptions.through),
                        (s1[0].paths[2], s2[3].paths[0], MovementOptions.left),
                        (s1[0].paths[1], s2[1].paths[0], MovementOptions.right),
                        (s1[2].paths[1], s1[3].paths[0], MovementOptions.through),
                        (s1[2].paths[2], s2[1].paths[0], MovementOptions.left),
                        (s1[2].paths[1], s2[3].paths[0], MovementOptions.right),
                        (s2[2].paths[1], s2[3].paths[0], MovementOptions.through),
                        (s2[2].paths[2], s1[3].paths[0], MovementOptions.left),
                        (s2[2].paths[1], s1[1].paths[0], MovementOptions.right),
                        (s2[0].paths[1], s2[1].paths[0], MovementOptions.through),
                        (s2[0].paths[2], s1[1].paths[0], MovementOptions.left),
                        (s2[0].paths[1], s1[3].paths[0], MovementOptions.right),]
    intersections.append(Intersection(s1 + s2, paths_to_connect))

for p in s_list[0].paths:
    print(p)