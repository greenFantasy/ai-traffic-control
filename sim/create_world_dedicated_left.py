from consts import *
from world import *
import time
import random
sys.path.append('../data')

world = DedicatedLeftTurnIntersectionWorld()
# random.seed(0)
world.add_vehicle_to_path(world.outer_north_lane_i_common, id = "carA")
world.add_vehicle_to_path(world.outer_south_lane_i_common, id = "carB")

streets = world.streets[::2]

for i in range(10000):
    world.play()
    if i % 20 == 0:
        r1 = random.randint(0, 3)
        r2 = random.randint(0, 1)
        path = streets[r1].paths[r2]
        if not path.aux_path:
            world.add_vehicle_to_path(path, id = f"car{i}")
