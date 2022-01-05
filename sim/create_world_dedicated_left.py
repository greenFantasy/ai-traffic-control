from consts import *
from world import *
import numpy as np
import time
import random
import sys
sys.path.append('../data')
sys.path.append('../generator')
from generator import MarkovGenerator
from map_creator import DynamicWorld

despawned = []

# for i in range(100):
world = DynamicWorld()# 0.8, split_times=[1.,1.,1.,1.], rl=True)
# world.set_spawnable_paths()
world.add_generator(MarkovGenerator(world, {"car2car": 0.03, "nocar2nocar": 0.99}))
# world.controllers[1].verbose = True
# random.seed(0)
# world.add_vehicle_to_path(world.outer_north_lane_i_common, id = "carA")
# world.add_vehicle_to_path(world.outer_south_lane_i_common, id = "carB")

# streets = world.streets[::2]

for i in range(5000):
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

# with open("../data/vehicle_despawn.csv", "r") as file:
#     despawned.append(len(file.readlines()))

# print("Mean: ", np.mean(despawned))
# print("Min: ", min(despawned))
# print("Max: ", max(despawned))
# print("Std: ", np.std(despawned))