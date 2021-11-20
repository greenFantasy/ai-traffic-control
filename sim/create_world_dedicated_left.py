from consts import *
from world import *
import time
import random
import sys
sys.path.append('../data')
sys.path.append('../generator')
from generator import SimpleGenerator

world = DedicatedLeftTurnIntersectionWorld(split_times=[8.,8.,8.,8.])
world.set_spawnable_paths()
world.add_generator(SimpleGenerator(world, {"p": 0.01}))
# random.seed(0)
# world.add_vehicle_to_path(world.outer_north_lane_i_common, id = "carA")
# world.add_vehicle_to_path(world.outer_south_lane_i_common, id = "carB")

# streets = world.streets[::2]

for i in range(2400):
    world.play()
    if i % 100 == 0:
        print(i)
    #     add_car = False
    #     while (not add_car):
    #         r1 = random.randint(0, 3)
    #         r2 = random.randint(0, 1)
    #         path = streets[r1].paths[r2]
    #         if not path.aux_path:
    #             world.add_vehicle_to_path(path, id = f"car{i}")
    #             add_car = True
print("Simulation complete")
world.close()